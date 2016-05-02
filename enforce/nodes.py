import typing
from abc import ABC, abstractmethod
import inspect

from .wrappers import EnforceProxy


class BaseNode(ABC):

    def __init__(self, data_type, strict, type_var=False):
        self.data_type = data_type
        self.strict = strict
        self.type_var = type_var

        self.data_out = None
        self.last_type = None
        self.original_children = []
        self.children = []

    def __str__(self):
        children_nest = ', '.join([str(c) for c in self.children])
        str_repr = '{}:{}'.format(str(self.data_type), self.__class__.__name__)
        if children_nest:
            str_repr += ' -> ({})'.format(children_nest)
        return str_repr

    def validate(self, data, validator, force=False):
        clean_data = self.preprocess_data(data)
        valid = self.validate_data(validator, clean_data, force)

        if not valid:
            yield False
            return

        results = []
        propagated_data = self.map_data(validator, clean_data)

        # Not using zip because it will silence a mismatch in sizes
        # between children and propagated_data
        # And, for now, at least, I'd prefer it be explicit
        # Note, if len(self.children) changes during iteration, errors *will* occur
        for i, child in enumerate(self.children):
            result = yield child.validate(propagated_data[i], validator, self.type_var)
            results.append(result)

        valid = all(results) if self.strict else any(results)

        if not valid:
            yield False
            return

        returned_data = [a.data_out for a in self.children]
        reduced_data = self.reduce_data(validator, returned_data, clean_data)

        self.data_out = self.postprocess_data(reduced_data)

        if results and force:
            self.children = [self.children[results.index(True)]]

        self.last_type = type(self.data_out)
        yield True

    def preprocess_data(self, data):
        """
        Prepares data for the other stages if needed
        """
        return data

    def postprocess_data(self, data):
        """
        Clears or updates data if needed after it was processed by all other stages
        """
        return data

    @abstractmethod
    def validate_data(self, validator, data, sticky=False) -> bool:
        """
        Responsible for determining if node is of specific type
        """
        pass

    @abstractmethod
    def map_data(self, validator, data):
        """
        Maps the input data to the nested type nodes
        """
        pass

    @abstractmethod
    def reduce_data(self, validator, data, old_data):
        """
        Combines the data from the nested type nodes into a current node expected data type
        """
        pass

    def add_child(self, child):
        self.children.append(child)
        self.original_children.append(child)

    def reset(self):
        self.data_out = None
        self.last_type = None
        self.children = [a for a in self.original_children]


class SimpleNode(BaseNode):

    def __init__(self, data_type):
        super().__init__(data_type, strict=True, type_var=False)

    def validate_data(self, validator, data, sticky=False):
        # Will keep till all the debugging is over
        #print('Simple Validation: {}:{}, {}\n=> {}'.format(
        #    data, type(data), self.data_type, issubclass(type(data),
        #                                                 self.data_type)))
        # This conditional is for when Callable object arguments are
        # mapped to SimpleNodes
        if isinstance(data, type):
            result = issubclass(data, self.data_type)
        else:
            result = issubclass(type(data), self.data_type)
        return result

    def map_data(self, validator, data):
        propagated_data = []
        if isinstance(data, list):
            # If it's a list we need to make child for every item in list
            propagated_data = data
            self.children *= len(data)
        return propagated_data

    def reduce_data(self, validator, data, old_data):
        return old_data


class UnionNode(BaseNode):

    def __init__(self):
        super().__init__(typing.Any, False)

    def validate_data(self, validator, data, sticky=False):
        # Will keep till all the debugging is over
        #print('Validation:', data, self.data_type)
        if sticky and self.last_type is not None:
            return type(data) == self.last_type
        return True

    def map_data(self, validator, data):
        output = []
        for _ in self.children:
            output.append(data)
        return output

    def reduce_data(self, validator, data, old_data):
        for element in data:
            if element is not None:
                return element
        return None


class TypeVarNode(BaseNode):
    # TODO: This node does not yet take covariant and contravariant properties
    # of the TypeVar into an account

    def __init__(self):
        super().__init__(typing.Any, False, True)

    def validate_data(self, validator, data, sticky=False):
        return True

    def map_data(self, validator, data):
        return [data]

    def reduce_data(self, validator, data, old_data):
        return data[0]


class TupleNode(BaseNode):

    def __init__(self):
        super().__init__(typing.Tuple, True)

    def validate_data(self, validator, data, sticky=False):
        if issubclass(type(data), self.data_type):
            return len(data) == len(self.children)
        else:
            return False

    def map_data(self, validator, data):
        output = []
        for element in data:
            output.append(element)
        return output

    def reduce_data(self, validator, data, old_data):
        return tuple(data)


class CallableNode(BaseNode):
    """
    This node is used when we have a function that expects another function
    as input. As an example:

        import typing
        def foo(func: typing.Callable[[int, int], int]) -> int:
            return func(5, 5)

    The typing.Callable type variable takes two parameters, the first being a
    list of its expected argument types with the second being its expected
    output type.
    """

    def __init__(self, data_type):
        super().__init__(data_type, strict=True, type_var=False)

    def preprocess_data(self, data):
        from .enforcers import Enforcer, apply_enforcer

        if not inspect.isfunction(data):
            return data

        try:
            enforcer = data.__enforcer__
        except AttributeError:
            proxy = EnforceProxy(data)
            return apply_enforcer(proxy)
        else:
            if isinstance(enforcer, Enforcer):
                return data
            else:
                return apply_enforcer(data)

    def validate_data(self, validator, data, sticky=False):
        # Will keep till all the debugging is over
        #print('Callable Validation: {}:{}, {}\n=> {}'.format(data, type(data),
        #                                       self.data_type,
        #                                       isinstance(data, self.data_type)))
        try:
            callable_signature = data.__enforcer__.callable_signature

            expected_params = self.data_type.__args__
            actual_params = callable_signature.__args__
            params_match = False

            if expected_params is None or expected_params is Ellipsis:
                params_match = True
            elif len(expected_params) == len(actual_params):
                for i, param_type in enumerate(expected_params):
                    if not issubclass(actual_params[i], param_type):
                        break
                else:
                    params_match = True

            expected_result = self.data_type.__result__
            actual_result = callable_signature.__result__
            result_match = False

            if expected_result is None or expected_result is Ellipsis:
                result_match = True
            else:
                result_match = issubclass(actual_result, expected_result)

            is_callable = params_match and result_match

            return is_callable
        except AttributeError:
            return False

    def map_data(self, validator, data):
        return []

    def reduce_data(self, validator, data, old_data):
        return old_data
