import typing
import inspect

from .wrappers import EnforceProxy
from .types import is_type_of_type, is_named_tuple
from .exceptions import RuntimeTypeError


class BaseNode:

    def __init__(self, data_type, is_sequence, type_var=False, covariant=None, contravariant=None):
        # is_sequence specifies if it is a sequence node
        # If it is not, then it must be a choice node, i.e. every children is a potential alternative
        # And at least one has to be satisfied
        # Sequence nodes implies all children must be satisfied
        self.data_type = data_type
        self.is_sequence = is_sequence
        self.type_var = type_var

        self.covariant = covariant
        self.contravariant = contravariant

        self.data_out = None
        self.out_type = None

        self.bound = False
        self.in_type = None

        self.original_children = []
        self.children = []

    def validate(self, data, validator, force=False):
        """
        Triggers all the stages of data validation, returning true or false as a result
        """
        # Validation steps:
        # 1. Pre-process (clean) incoming data
        # 2. Validate data
        # 3. If validated, map (distribute) data to child nodes. Otherwise - FAIL.
        # 4. Validate data at each node
        # 5. If sequence, all nodes must successfully validate date. Otherwise, at least one.
        # 6. If validated, reduce (collect) data from child nodes. Otherwise - FAIL.
        # 7. Post-process (clean) the resultant data
        # 8. Sets the output data for the node
        # 9. Indicate validation SUCCESS
        clean_data = self.preprocess_data(validator, data)

        valid = self.validate_data(validator, clean_data, force)

        if not valid:
            yield False
            return

        propagated_data = self.map_data(validator, clean_data)

        validation_results, returned_data = yield self.validate_children(validator, propagated_data)

        valid = all(validation_results) if self.is_sequence else any(validation_results)

        if not valid:
            yield False
            return

        reduced_data = self.reduce_data(validator, returned_data, clean_data)

        data_out = self.postprocess_data(validator, reduced_data)

        self.set_out_data(validator, data, data_out)

        yield True

    def validate_children(self, validator, propagated_data):
        """
        Performs the validation of child nodes and collects their results
        This is a default implementation and it requires the size of incoming values to match the number of children
        """
        # Not using zip because it will silence a mismatch in sizes
        # between children and propagated_data
        # And, for now, at least, I'd prefer it being explicit
        # Note, if len(self.children) changes during iteration, errors *will* occur
        children_validation_results = []
        children_data_out = []

        for i, child in enumerate(self.children):
            result = yield child.validate(propagated_data[i], validator, self.type_var)
            children_validation_results.append(result)
            children_data_out.append(child.data_out)
        
        yield children_validation_results, children_data_out

    def set_out_data(self, validator, in_data, out_data):
        """
        Sets the output data for the node to the combined data of its children
        Also sets the type of a last processed node
        """
        self.in_type = type(in_data)
        self.data_out = out_data
        self.out_type = type(out_data)

    def preprocess_data(self, validator, data):
        """
        Prepares data for the other stages if needed
        """
        return data

    def postprocess_data(self, validator, data):
        """
        Clears or updates data if needed after it was processed by all other stages
        """
        return data

    def validate_data(self, validator, data, sticky=False) -> bool:
        """
        Responsible for determining if node is of specific type
        """
        return False

    def map_data(self, validator, data):
        """
        Maps the input data to the nested type nodes
        """
        return []

    def reduce_data(self, validator, data, old_data):
        """
        Combines the data from the nested type nodes into a current node expected data type
        """
        return old_data

    def add_child(self, child):
        """
        Adds a new child node and saves it in the original_children list
        in order to be able to restore the original list
        """
        self.children.append(child)
        self.original_children.append(child)

    def reset(self):
        """
        Resets the node state to its original, including the order and number of child nodes
        """
        self.bound = False
        self.in_type = None
        self.data_out = None
        self.out_type = None
        self.children = [a for a in self.original_children]

    def __repr__(self):
        children_nest = ', '.join([str(c) for c in self.children])
        str_repr = '{}:{}'.format(str(self.data_type), self.__class__.__name__)
        if children_nest:
            str_repr += ' -> ({})'.format(children_nest)
        return str_repr


class SimpleNode(BaseNode):

    def __init__(self, data_type, **kwargs):
        super().__init__(data_type, is_sequence=True, type_var=False, **kwargs)

    def validate_data(self, validator, data, sticky=False):
        # Will keep till all the debugging is over
        #print('Simple Validation: {}:{}, {}\n=> {}'.format(
        #    data, type(data), self.data_type, issubclass(type(data),
        #                                                 self.data_type)))
        # This conditional is for when Callable object arguments are
        # mapped to SimpleNodes
        if self.bound:
            data_type = self.in_type
        else:
            data_type = self.data_type

        # TODO: Is everything we are interested in converting to type, is an instance of Type?
        if not isinstance(data, type):
            data = type(data)

        covariant = self.covariant or validator.settings.covariant
        contravariant = self.contravariant or validator.settings.contravariant

        return is_type_of_type(data, data_type, covariant=covariant, contravariant=contravariant)

    def map_data(self, validator, data):
        propagated_data = []
        if isinstance(data, list):
            # If it's a list we need to make child for every item in list
            propagated_data = data
            self.children = len(data) * self.original_children
        return propagated_data


class UnionNode(BaseNode):
    """
    A special node - it not only tests for the union type,
    It is also used with type variables
    """

    def __init__(self, **kwargs):
        super().__init__(typing.Any, is_sequence=False, **kwargs)

    def validate_data(self, validator, data, sticky=False):
        # Will keep till all the debugging is over
        #print('Validation:', data, type(data), self.data_type, self.last_type)
        #if sticky and (self.last_type is not None):
        #    return is_type_of_type(type(data),
        #                           self.last_type,
        #                           covariant=self.covariant,
        #                           contravariant=self.contravariant)
        return True

    def map_data(self, validator, data):
        return [data for _ in self.children]

    def reduce_data(self, validator, data, old_data):
        return next((element for element in data if element is not None), None)


class TypeVarNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(data_type=None, is_sequence=True, type_var=True, **kwargs)

    def validate_data(self, validator, data, sticky=False):
        return True

    def map_data(self, validator, data):
        return [data for _ in self.children]

    def reduce_data(self, validator, data, old_data):
        # Returns first non-None element, or None if every element is None
        return next((element for element in data if element is not None), None)

    def validate_children(self, validator, propagated_data):
        children_validation_results = []
        children_data_out = []

        for i, child in enumerate(self.children):
            result = yield child.validate(propagated_data[i], validator, self.type_var)
            if result:
                children_validation_results.append(result)
                children_data_out.append(child.data_out)
                if not self.bound:
                    self.bound = True
                    self.children = [child]
                if child.data_type is typing.Any:
                    child.bound = True
                break
        else:
            children_validation_results.append(False)
            children_data_out.append(None)
        
        yield children_validation_results, children_data_out

    def add_child(self, child):
        child.covariant = self.covariant
        child.contravariant = self.contravariant
        super().add_child(child)


class TupleNode(BaseNode):

    def __init__(self, variable_length=False, **kwargs):
        self.variable_length = variable_length
        super().__init__(typing.Tuple, is_sequence=True, **kwargs)

    def validate_data(self, validator, data, sticky=False):
        covariant = self.covariant or validator.settings.covariant
        contravariant = self.contravariant or validator.settings.contravariant

        if is_type_of_type(type(data), self.data_type, covariant=covariant, contravariant=contravariant):
            if self.variable_length:
                return True
            else:
                return len(data) == len(self.children)
        else:
            return False

    def validate_children(self, validator, propagated_data):
        if self.variable_length:
            child = self.children[0]

            children_validation_results = []
            children_data_out = []

            for i, data in enumerate(propagated_data):
                result = yield child.validate(data, validator, self.type_var)
                children_validation_results.append(result)
                children_data_out.append(child.data_out)
        
            yield children_validation_results, children_data_out
        else:
            yield super().validate_children(validator, propagated_data)

    def map_data(self, validator, data):
        output = []
        for element in data:
            output.append(element)
        return output

    def reduce_data(self, validator, data, old_data):
        return tuple(data)


class NamedTupleNode(BaseNode):

    def __init__(self, data_type, **kwargs):
        from .decorators import runtime_validation

        super().__init__(runtime_validation(data_type), is_sequence=True, **kwargs)

    def preprocess_data(self, validator, data):
        if not is_named_tuple(data): return None
        if type(data).__name__ != self.data_type.__name__: return None

        if hasattr(data, '_field_types') != hasattr(self.data_type, '_field_types'): return None

        try:
            return self.data_type(*(getattr(data, field) for field in data._fields))
        except RuntimeTypeError:
            return None
        except AttributeError:
            return None
        except TypeError:
            return None

    def validate_data(self, validator, data, sticky=False):
        return bool(data)


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

    def __init__(self, data_type, **kwargs):
        super().__init__(data_type, is_sequence=True, type_var=False, **kwargs)

    def preprocess_data(self, validator, data):
        from .enforcers import Enforcer, apply_enforcer

        if not inspect.isfunction(data):
            if hasattr(data, '__call__'): # handle case where data is a callable object
                data = data.__call__
            else:
                return data

        try:
            enforcer = data.__enforcer__
        except AttributeError:
            proxy = EnforceProxy(data)
            return apply_enforcer(proxy)
        else:
            covariant = self.covariant or validator.settings.covariant
            contravariant = self.contravariant or validator.settings.contravariant

            if is_type_of_type(type(enforcer), Enforcer, covariant=covariant, contravariant=contravariant):
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
                    if actual_params[i] != param_type:
                        break
                else:
                    params_match = True

            expected_result = self.data_type.__result__
            actual_result = callable_signature.__result__
            result_match = False

            if expected_result is None or expected_result is Ellipsis:
                result_match = True
            else:
                result_match = type(actual_result) == type(expected_result)

            is_callable = params_match and result_match

            return is_callable
        except AttributeError:
            return False
        except TypeError:
            # Can occur in case of typing.Callable having no parameters
            return False


class GenericNode(BaseNode):

    def __init__(self, data_type, **kwargs):
        from .enforcers import Enforcer, GenericProxy
        
        try:
            enforcer = data_type.__enforcer__
        except AttributeError:
            enforcer = GenericProxy(data_type).__enforcer__
        else:
            covariant = self.covariant or validator.settings.covariant
            contravariant = self.contravariant or validator.settings.contravariant

            if not is_type_of_type(type(enforcer), Enforcer, covariant=covariant, contravariant=contravariant):
                enforcer =  GenericProxy(data_type).__enforcer__

        super().__init__(enforcer, is_sequence=True, type_var=False, **kwargs)

    def preprocess_data(self, validator, data):
        from .enforcers import Enforcer, GenericProxy

        try:
            enforcer = data.__enforcer__
        except AttributeError:
            return GenericProxy(data)
        else:
            covariant = self.covariant or validator.settings.covariant
            contravariant = self.contravariant or validator.settings.contravariant

            if is_type_of_type(type(enforcer), Enforcer, covariant=covariant, contravariant=contravariant):
                return data
            else:
                return GenericProxy(data)

    def validate_data(self, validator, data, sticky=False):
        enforcer = data.__enforcer__

        covariant = self.covariant or validator.settings.covariant
        contravariant = self.contravariant or validator.settings.contravariant

        if not is_type_of_type(enforcer.signature,
                               self.data_type.signature,
                               covariant=covariant,
                               contravariant=contravariant):
            return False

        if self.data_type.bound != enforcer.bound:
            return False

        if len(enforcer.hints) != len(self.data_type.hints):
            return False

        for hint_name, hint_value in enforcer.hints.items():
            hint = self.data_type.hints[hint_name]
            if hint != hint_value:
                for constraint in hint_value.constraints:
                    if is_type_of_type(constraint, hint, covariant=covariant, contravariant=contravariant):
                        break
                else:
                    return False

        return True
