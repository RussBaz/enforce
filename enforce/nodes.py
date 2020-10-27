import inspect
import typing

from . import domain_types as dt
from .types import is_type_of_type, is_named_tuple
from .wrappers import EnforceProxy

TYPE_NAME_ALIASES = {
    "Tuple": "typing.Tuple",
    "tuple": "typing.Tuple",
    "List": "typing.List",
    "list": "typing.List",
    "Set": "typing.Set",
    "set": "typing.Set",
    "Dict": "typing.Dict",
    "dict": "typing.Dict",
}


class BaseNode:
    def __init__(
        self,
        expected_data_type: type,
        is_sequence: bool,
        is_container: bool = False,
        is_forward_ref: bool = None,
        type_var: bool = False,
        covariant: typing.Optional[bool] = None,
        contravariant: typing.Optional[bool] = None,
    ):
        # is_sequence specifies if it is a sequence node
        # If it is not, then it must be a choice node, i.e. every children is a potential alternative
        # And at least one has to be satisfied
        # Sequence nodes implies all children must be satisfied
        self.expected_data_type = expected_data_type
        self.is_sequence = is_sequence
        self.is_type_var = type_var
        self.is_forward_ref = is_forward_ref
        self.is_container = is_container

        self.covariant = covariant
        self.contravariant = contravariant

        self.data_out = None

        # TypeVar stuff
        self.bound = False
        self.in_type = None

        self.original_children = []
        self.children = []

    def validate_children(
        self, validator: "Validator", propagated_data: typing.Any
    ) -> typing.List[dt.ValidationResult]:
        """
        Performs the validation of child nodes and collects their results
        This is a default implementation and it requires the size of incoming values to match the number of children
        """
        # Not using zip because it will silence a mismatch in sizes
        # between children and propagated_data
        # And, for now, at least, I'd prefer it being explicit
        # Note, if len(self.children) changes during iteration, errors *will* occur
        children_validation_results = []

        number_of_children = len(self.children)

        if len(propagated_data) < len(self.children):
            for i, data in enumerate(propagated_data):
                validation_result = yield validator.validate_lazy(
                    self.children[i], data, self.is_type_var
                )
                children_validation_results.append(validation_result)
        elif len(propagated_data) > len(self.children):
            number_of_extra_elements = len(propagated_data) - len(self.children)
            for i, child in enumerate(self.children):
                validation_result = yield validator.validate_lazy(
                    child, propagated_data[i], self.is_type_var
                )
                children_validation_results.append(validation_result)
            if self.bound or not self.expected_data_type is typing.Any:
                for i in range(number_of_extra_elements):
                    data = propagated_data[number_of_children + i]
                    children_validation_results.append(
                        dt.ValidationResult(False, data, extract_type_name(data))
                    )
        else:
            for i, child in enumerate(self.children):
                validation_result = yield validator.validate_lazy(
                    child, propagated_data[i], self.is_type_var
                )
                children_validation_results.append(validation_result)

        yield children_validation_results

    def get_actual_data_type(
        self, self_validation_result, child_validation_results, valid
    ):
        """
        Returns a name of an actual type of given data
        """
        actual_type = self_validation_result.type_name
        child_types = set(result.type_name for result in child_validation_results)

        child_types.discard(None)

        actual_type = TYPE_NAME_ALIASES.get(actual_type, actual_type)

        if child_types:
            actual_type = actual_type + "[" + ", ".join(child_types) + "]"

        return actual_type

    def set_out_data(self, validator: "Validator", in_data, out_data):
        """
        Sets the output data for the node to the combined data of its children
        Also sets the type of a last processed node
        """
        self.in_type = type(in_data)
        self.data_out = out_data

    def preprocess_data(self, validator: "Validator", data):
        """
        Prepares data for the other stages if needed
        """
        return data

    def postprocess_data(self, validator: "Validator", data):
        """
        Clears or updates data if needed after it was processed by all other stages
        """
        return data

    def validate_data(self, validator: "Validator", data, sticky=False) -> bool:
        """
        Responsible for determining if node is of specific type
        """
        return dt.ValidationResult(
            valid=False, data=data, type_name=extract_type_name(data)
        )

    def map_data(self, validator: "Validator", self_validation_result):
        """
        Maps the input data to the nested type nodes
        """
        return []

    def reduce_data(
        self, validator: "Validator", self_validation_result, child_validation_results
    ):
        """
        Combines the data from the nested type nodes into a current node expected data type
        """
        return self_validation_result.data

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
        self.children = [a for a in self.original_children]

    def __repr__(self):
        children_nest = ", ".join([str(c) for c in self.children])
        str_repr = "{}:{}".format(str(self.expected_data_type), self.__class__.__name__)
        if children_nest:
            str_repr += " -> ({})".format(children_nest)
        return str_repr


class SimpleNode(BaseNode):
    def __init__(self, expected_data_type, **kwargs):
        super().__init__(expected_data_type, is_sequence=True, type_var=False, **kwargs)

    def validate_data(self, validator: "Validator", data, sticky=False):
        if self.bound:
            expected_data_type = self.in_type
        else:
            expected_data_type = self.expected_data_type

        # TODO: Is everything we are interested in converting to type, is an instance of Type?
        if not isinstance(data, type):
            input_type = type(data)
        else:
            input_type = data

        covariant = self.covariant or validator.settings.covariant
        contravariant = self.contravariant or validator.settings.contravariant

        result = is_type_of_type(
            input_type,
            expected_data_type,
            covariant=covariant,
            contravariant=contravariant,
        )

        type_name = input_type.__name__

        type_name = TYPE_NAME_ALIASES.get(type_name, type_name)

        if expected_data_type is not None and hasattr(expected_data_type, '__origin__') and expected_data_type.__origin__ == typing.Literal and data in frozenset(expected_data_type.__args__):
            result, type_name = True, expected_data_type
        return dt.ValidationResult(valid=result, data=data, type_name=type_name)

    def map_data(self, validator: "Validator", self_validation_result):
        data = self_validation_result.data
        propagated_data = []
        if isinstance(data, list):
            # If it's a list we need to make child for every item in list
            propagated_data = data
            self.children = len(data) * self.original_children

        if isinstance(data, set):
            # If it's a list we need to make child for every item in list
            propagated_data = list(data)
            self.children = len(data) * self.original_children
        return propagated_data


class UnionNode(BaseNode):
    """
    A special node - it not only tests for the union type,
    It is also used with type variables
    """

    def __init__(self, **kwargs):
        super().__init__(typing.Any, is_sequence=False, is_container=True, **kwargs)

    def validate_data(self, validator: "Validator", data, sticky=False):
        return dt.ValidationResult(
            valid=True, data=data, type_name=extract_type_name(data)
        )

    def map_data(self, validator: "Validator", self_validation_result):
        return [self_validation_result.data for _ in self.children]

    def reduce_data(
        self, validator: "Validator", self_validation_result, child_validation_result
    ):
        return next(
            (
                result.data
                for result in child_validation_result
                if result.data is not None
            ),
            None,
        )

    def get_actual_data_type(
        self, self_validation_result, child_validation_results, valid
    ):
        """
        Returns a name of an actual type of given data
        """
        # actual_type = self_validation_result.type_name
        child_types = set(result.type_name for result in child_validation_results)

        child_types.discard(None)

        return child_types.pop()


class TypeVarNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(
            expected_data_type=None, is_sequence=True, type_var=True, **kwargs
        )

    def validate_data(self, validator: "Validator", data, sticky=False):
        return dt.ValidationResult(valid=True, data=data, type_name="typing.TypeVar")

    def map_data(self, validator: "Validator", self_validation_result):
        return [self_validation_result.data for _ in self.children]

    def reduce_data(
        self, validator: "Validator", self_validation_result, child_validation_results
    ):
        # Returns first non-None element, or None if every element is None
        return next(
            (
                result.data
                for result in child_validation_results
                if result.data is not None
            ),
            None,
        )

    def validate_children(self, validator: "Validator", propagated_data):
        children_validation_results = []

        for i, child in enumerate(self.children):
            validation_result = yield validator.validate_lazy(
                child, propagated_data[i], self.is_type_var
            )
            if validation_result.valid:
                children_validation_results.append(validation_result)
                if not self.bound:
                    self.bound = True
                    self.children = [child]
                if child.expected_data_type is typing.Any:
                    child.bound = True
                break
        else:
            children_validation_results.append(
                dt.ValidationResult(False, propagated_data[0], None)
            )

        yield children_validation_results

    def add_child(self, child):
        child.covariant = self.covariant
        child.contravariant = self.contravariant
        super().add_child(child)


class TupleNode(BaseNode):
    def __init__(self, variable_length=False, **kwargs):
        self.variable_length = variable_length
        super().__init__(typing.Tuple, is_sequence=True, is_container=True, **kwargs)

    def validate_data(self, validator: "Validator", data, sticky=False):
        # fix for https://github.com/RussBaz/enforce/issues/62 (1/4)
        if data is None:
            # unfortunately this is not enough to stop propagating to children...
            # ... so the None case is also handled in map_data and validate_children
            return dt.ValidationResult(
                valid=False, data=data, type_name=extract_type_name(type(data))
            )

        covariant = self.covariant or validator.settings.covariant
        contravariant = self.contravariant or validator.settings.contravariant

        input_type = type(data)

        if is_type_of_type(
            input_type,
            self.expected_data_type,
            covariant=covariant,
            contravariant=contravariant,
        ):
            if self.variable_length:
                return dt.ValidationResult(
                    valid=True, data=data, type_name=extract_type_name(input_type)
                )
            else:
                return dt.ValidationResult(
                    valid=len(data) == len(self.children),
                    data=data,
                    type_name=extract_type_name(input_type),
                )
        else:
            return dt.ValidationResult(
                valid=False, data=data, type_name=extract_type_name(input_type)
            )

    def validate_children(self, validator: "Validator", propagated_data):
        # fix for https://github.com/RussBaz/enforce/issues/62 (3/4)
        if propagated_data is None:
            # yield a sequence of one element: a single failure
            yield [
                dt.ValidationResult(
                    valid=False,
                    data=propagated_data,
                    type_name=extract_type_name(propagated_data),
                )
            ]
        elif self.variable_length:
            child = self.children[0]

            children_validation_results = []

            for i, data in enumerate(propagated_data):
                validation_result = yield validator.validate_lazy(
                    child, data, self.is_type_var
                )
                children_validation_results.append(validation_result)

            yield children_validation_results
        else:
            yield super().validate_children(validator, propagated_data)

    def map_data(self, validator: "Validator", self_validation_result):
        data = self_validation_result.data
        # fix for https://github.com/RussBaz/enforce/issues/62 (2/4)
        if data is not None:
            output = []
            for element in data:
                output.append(element)
            return output
        else:
            return None

    def reduce_data(
        self, validator: "Validator", self_validation_result, child_validation_results
    ):
        return tuple(result.data for result in child_validation_results)

    def get_actual_data_type(
        self, self_validation_result, child_validation_results, valid
    ):
        """
        Returns a name of an actual type of given data
        """
        actual_type = self_validation_result.type_name

        # fix for https://github.com/RussBaz/enforce/issues/62 (4/4)
        if actual_type == extract_type_name(type(None)):
            # None - No need to check children
            actual_type = TYPE_NAME_ALIASES.get(actual_type, actual_type)

        else:
            # Append children type information
            child_types = (
                list(result.type_name for result in child_validation_results) or []
            )

            actual_type = TYPE_NAME_ALIASES.get(actual_type, actual_type)

            if child_types:
                actual_type = actual_type + "[" + ", ".join(child_types) + "]"

        return actual_type


class NamedTupleNode(BaseNode):
    def __init__(self, data_type, exception_type, **kwargs):
        from .decorators import runtime_validation

        super().__init__(
            runtime_validation(data_type), is_sequence=True, is_container=True, **kwargs
        )
        self.data_type_name = None
        self.exception_type = exception_type

    def preprocess_data(self, validator: "Validator", data):
        data_type = type(data)

        self.data_type_name = data_type.__name__

        if not is_named_tuple(data):
            return None

        if data_type.__name__ != self.expected_data_type.__name__:
            return None

        if not hasattr(data, "_field_types"):
            self.data_type_name = "untyped " + data_type.__name__
            return None

        try:
            return self.expected_data_type(
                *(getattr(data, field) for field in data._fields)
            )
        except self.exception_type:
            self.data_type_name = (
                str(type(data))
                + " with incorrect arguments: "
                + ", ".join(
                    field + " -> " + str(type(getattr(data, field)))
                    for field in data._fields
                )
            )
            return None
        except AttributeError:
            return None
        except TypeError:
            return None

    def validate_data(self, validator: "Validator", data, sticky=False):
        if data is None:
            data_type_name = self.data_type_name
        else:
            data_type_name = type(data).__name__

        data_type_name = TYPE_NAME_ALIASES.get(data_type_name, data_type_name)

        return dt.ValidationResult(
            valid=bool(data), data=data, type_name=data_type_name
        )


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
        super().__init__(
            data_type, is_sequence=True, is_container=True, type_var=False, **kwargs
        )

    def preprocess_data(self, validator: "Validator", data):
        from .enforcers import Enforcer, apply_enforcer

        covariant = self.covariant or validator.settings.covariant
        contravariant = self.contravariant or validator.settings.contravariant

        try:
            if not inspect.isroutine(data):
                if inspect.ismethod(data.__call__):
                    data = data.__call__
                else:
                    return data
        except AttributeError:
            return data

        mutable = hasattr(data, "__dict__")

        try:
            enforcer = data.__enforcer__
        except AttributeError:
            enforcer = None
            data = EnforceProxy(data)
        else:
            if not mutable:
                data = EnforceProxy(data)

        if not is_type_of_type(
            type(enforcer), Enforcer, covariant=covariant, contravariant=contravariant
        ):
            data = apply_enforcer(data, settings=validator.settings)

        return data

    def validate_data(self, validator: "Validator", data, sticky=False):
        try:
            input_type = type(data)

            callable_signature = data.__enforcer__.callable_signature

            if self.expected_data_type.__args__ is None:
                expected_params = []
            elif self.expected_data_type.__args__ is Ellipsis:
                expected_params = [Ellipsis]
            else:
                expected_params = list(self.expected_data_type.__args__)

            if callable_signature.__args__ is None:
                actual_params = []
            else:
                actual_params = list(callable_signature.__args__)

            params_match = False

            try:
                if self.expected_data_type.__result__ is not None:
                    expected_params.append(self.expected_data_type.__result__)

                if callable_signature.__result__ is not None:
                    actual_params.append(callable_signature.__result__)
            except AttributeError:
                pass

            try:
                if len(expected_params) == 0:
                    params_match = True
                elif expected_params[0] is Ellipsis and len(actual_params) > 0:
                    params_match = actual_params[-1] == expected_params[-1]
                elif len(expected_params) == len(actual_params):
                    for i, param_type in enumerate(expected_params):
                        if actual_params[i] != param_type:
                            break
                    else:
                        params_match = True

                return dt.ValidationResult(
                    valid=params_match, data=data, type_name=str(callable_signature)
                )
            except AttributeError:
                return dt.ValidationResult(
                    valid=False, data=data, type_name=str(callable_signature)
                )
        except AttributeError:
            return dt.ValidationResult(
                valid=False, data=data, type_name=extract_type_name(input_type)
            )


class GenericNode(BaseNode):
    def __init__(self, data_type, **kwargs):
        from .enforcers import Enforcer, GenericProxy

        try:
            enforcer = data_type.__enforcer__
        except AttributeError:
            enforcer = GenericProxy(data_type).__enforcer__
        else:
            covariant = kwargs["covariant"]
            contravariant = kwargs["contravariant"]

            if not is_type_of_type(
                type(enforcer),
                Enforcer,
                covariant=covariant,
                contravariant=contravariant,
            ):
                enforcer = GenericProxy(data_type).__enforcer__

        super().__init__(
            enforcer, is_sequence=True, is_container=True, type_var=False, **kwargs
        )

    def preprocess_data(self, validator: "Validator", data):
        from .enforcers import Enforcer, GenericProxy

        try:
            enforcer = data.__enforcer__
        except AttributeError:
            return GenericProxy(data)
        else:
            covariant = self.covariant or validator.settings.covariant
            contravariant = self.contravariant or validator.settings.contravariant

            if is_type_of_type(
                type(enforcer),
                Enforcer,
                covariant=covariant,
                contravariant=contravariant,
            ):
                return data
            else:
                return GenericProxy(data)

    def validate_data(self, validator: "Validator", data, sticky=False):
        enforcer = data.__enforcer__
        input_type = enforcer.signature

        covariant = self.covariant or validator.settings.covariant
        contravariant = self.contravariant or validator.settings.contravariant

        if not is_type_of_type(
            input_type,
            self.expected_data_type.signature,
            covariant=covariant,
            contravariant=contravariant,
        ):
            return dt.ValidationResult(valid=False, data=data, type_name=input_type)

        if self.expected_data_type.bound != enforcer.bound:
            return dt.ValidationResult(valid=False, data=data, type_name=input_type)

        if len(enforcer.hints) != len(self.expected_data_type.hints):
            return dt.ValidationResult(valid=False, data=data, type_name=input_type)

        for hint_name, hint_value in enforcer.hints.items():
            hint = self.expected_data_type.hints[hint_name]
            if hint != hint_value:
                for constraint in hint_value.constraints:
                    if is_type_of_type(
                        constraint,
                        hint,
                        covariant=covariant,
                        contravariant=contravariant,
                    ):
                        break
                else:
                    return dt.ValidationResult(
                        valid=False, data=data, type_name=input_type
                    )

        return dt.ValidationResult(valid=True, data=data, type_name=input_type)


class MappingNode(BaseNode):
    def __init__(self, data_type, **kwargs):
        super().__init__(data_type, is_sequence=True, is_container=True, **kwargs)

    def validate_data(self, validator: "Validator", data, sticky=False):
        if not isinstance(data, type):
            input_type = type(data)
        else:
            input_type = data

        covariant = self.covariant or validator.settings.covariant
        contravariant = self.contravariant or validator.settings.contravariant

        result = is_type_of_type(
            input_type,
            self.expected_data_type,
            covariant=covariant,
            contravariant=contravariant,
        )

        type_name = input_type.__name__
        return dt.ValidationResult(valid=result, data=data, type_name=type_name)

    def validate_children(self, validator: "Validator", propagated_data):
        key_validator = self.children[0]
        value_validator = self.children[1]

        children_validation_results = []

        for i, data in enumerate(propagated_data):
            key_validation_result = yield validator.validate_lazy(
                key_validator, data[0], self.is_type_var
            )
            value_validation_result = yield validator.validate_lazy(
                value_validator, data[1], self.is_type_var
            )

            is_valid = key_validation_result.valid and value_validation_result.valid
            out_data = (key_validation_result.data, value_validation_result.data)
            out_name = (
                key_validation_result.type_name,
                value_validation_result.type_name,
            )

            out_name = [TYPE_NAME_ALIASES.get(n, n) for n in out_name]

            out_result = dt.ValidationResult(
                valid=is_valid, data=out_data, type_name=out_name
            )

            children_validation_results.append(out_result)

        yield children_validation_results

    def map_data(self, validator: "Validator", self_validation_result):
        data = self_validation_result.data
        output = []
        if self_validation_result.valid:
            for item_pair in data.items():
                output.append(item_pair)

        return output

    def reduce_data(
        self, validator: "Validator", self_validation_result, child_validation_results
    ):
        return {result.data[0]: result.data[1] for result in child_validation_results}

    def get_actual_data_type(
        self, self_validation_result, child_validation_results, valid
    ):
        """
        Returns a name of an actual type of given data
        """
        actual_type = self_validation_result.type_name

        actual_type = TYPE_NAME_ALIASES.get(actual_type, actual_type)

        key_types = (
            set(result.type_name[0] for result in child_validation_results) or set()
        )
        value_types = (
            set(result.type_name[1] for result in child_validation_results) or set()
        )

        key_types = sorted(key_types)
        value_types = sorted(value_types)

        if len(key_types) > 1:
            key_type = "typing.Union[" + ", ".join(key_types) + "]"
        elif len(key_types) == 1:
            key_type = key_types[0]
        else:
            return actual_type

        if len(value_types) > 1:
            value_type = "typing.Union[" + ", ".join(value_types) + "]"
        elif len(value_types) == 1:
            value_type = value_types[0]
        else:
            return actual_type

        actual_type = actual_type + "[" + key_type + ", " + value_type + "]"

        return actual_type


class ForwardRefNode(BaseNode):
    """
    Forward Reference node - when validate is called for the first time,
    it permanently adds a child to itself with an actual node
    for the evaluated type of a provided ForwardRef
    """

    def __init__(self, forward_ref, **kwargs):
        super().__init__(
            typing.Any,
            is_sequence=False,
            is_container=True,
            is_forward_ref=True,
            **kwargs
        )
        self.forward_ref = forward_ref

    def validate_data(self, validator: "Validator", data, sticky=False):
        return dt.ValidationResult(
            valid=True, data=data, type_name=extract_type_name(data)
        )

    def map_data(self, validator: "Validator", self_validation_result):
        return [self_validation_result.data]

    def reduce_data(
        self, validator: "Validator", self_validation_result, child_validation_result
    ):
        return child_validation_result[0].data

    def get_actual_data_type(
        self, self_validation_result, child_validation_results, valid
    ):
        """
        Returns a name of an actual type of given data
        """
        return child_validation_results[0].type_name


def extract_type_name(data):
    if isinstance(data, type):
        type_name = data.__name__
    else:
        type_name = type(data).__name__

    return TYPE_NAME_ALIASES.get(type_name, type_name)
