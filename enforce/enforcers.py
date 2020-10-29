import inspect
import typing
from collections import namedtuple, OrderedDict

from wrapt import ObjectProxy

from .settings import Settings
from .types import EnhancedTypeVar, is_type_of_type
# from .wrappers import Proxy, EnforceProxy
# from .exceptions import RuntimeTypeError
from .validator import init_validator, Validator

# This TypeVar is used to indicate that he result of output validation
# is the same as the input to the output validation
T = typing.TypeVar("T")

# Convenience type for storing all incoming arguments in a single container
Parameters = namedtuple("Parameters", ["args", "kwargs", "skip"])


class Enforcer:
    """
    A container for storing type checking logic of functions
    """

    def __init__(
        self,
        name,
        validator,
        signature,
        hints,
        generic=False,
        bound=False,
        settings=None,
    ):
        self.name = name
        self.validator = validator
        self.signature = signature
        self.hints = hints
        self.settings = settings

        self.validator.settings = self.settings

        self.generic = generic
        self.bound = bound

        self.reference = None

        self._callable_signature = None

    @property
    def callable_signature(self):
        """
        A property which returns _callable_signature (Callable type of the function)
        If it is None, then it generates a new Callable type from the object's signature
        """
        if self.settings is not None and not self.settings:
            return typing.Callable

        if hasattr(self.reference, "__no_type_check__"):
            return typing.Callable

        if self._callable_signature is None:
            self._callable_signature = generate_callable_from_signature(self.signature)

        return self._callable_signature

    def validate_inputs(self, input_data: Parameters) -> Parameters:
        """
        Calls a validator for each function argument
        """
        if self.settings is not None and not self.settings.enabled:
            return input_data

        if input_data.skip:
            return input_data

        args = input_data.args
        kwargs = input_data.kwargs
        skip = input_data.skip

        try:
            bind_arguments = self.signature.bind(*args, **kwargs)
        except TypeError as e:
            message = str(e)

            if message == "too many positional arguments":
                new_message = (
                    self.name
                    + str(self.signature)
                    + " was given an incorrect number of positional arguments"
                )
                raise TypeError(new_message)
            else:
                raise e

        bind_arguments.apply_defaults()

        for name in self.hints.keys():
            # First, check argument types (every key not labeled 'return')
            if name != "return":
                argument = bind_arguments.arguments.get(name)
                if not self.validator.validate(argument, name):
                    break
                bind_arguments.arguments[name] = self.validator.data_out[name]
        else:
            validated_data = Parameters(
                bind_arguments.args, bind_arguments.kwargs, skip
            )
            return validated_data

        process_errors(self.settings, self.validator.errors, self.hints)

    def validate_outputs(self, output_data: T) -> T:
        """
        Calls a validator on a function return value
        """
        if self.settings is not None and not self.settings.enabled:
            return output_data

        if "return" in self.hints.keys():
            if not self.validator.validate(output_data, "return"):
                process_errors(self.settings, self.validator.errors, self.hints, True)
            else:
                return self.validator.data_out["return"]
        else:
            return output_data

    def set_outer_scope_variables(self, outer_locals, outer_globals):
        """
        Sets the reference to the outer scope on a validator
        This allows an access to the outer execution scope
        which is not known at definition time
        This also enables the forward referencing
        """
        self.validator.locals = outer_locals
        self.validator.globals = outer_globals

    def reset(self):
        """
        Clears validator internal state
        """
        self.validator.reset()


class GenericProxy(ObjectProxy):
    """
    A proxy object for typing.Generics user defined subclasses which always returns proxy-d objects
    """

    __enforcer__ = None

    def __init__(self, wrapped, settings=None):
        """
        Creates an enforcer instance on a just wrapped user defined Generic
        """
        wrapped_type = type(wrapped)
        if settings is None:
            self._self_settings = Settings(enabled=True, group="default")
        else:
            self._self_settings = settings

        # Does anyone remember what exactly this piece of code checks? [Russ]
        # Note to myself:
        # First case is to prevent wrapping already wrapped objects
        # Second case is to find out if it is actually a Generic or something else
        # Because only Generics are allowed to be wrapped by a Generic proxy
        if is_type_of_type(wrapped_type, GenericProxy):
            super().__init__(wrapped.__wrapped__)
            self.__enforcer__ = get_enforcer(
                self, generic=True, instance_of=self, settings=self._self_settings
            )
        elif is_type_of_type(wrapped_type, typing.GenericMeta):
            super().__init__(wrapped)
            self.__enforcer__ = get_enforcer(self, generic=True, settings=self._self_settings)
        else:
            raise TypeError("Only generics can be wrapped in GenericProxy")

    def __call__(self, *args, **kwargs):
        self.__enforcer__ = get_enforcer(
            self.__wrapped__(*args, **kwargs),
            generic=True,
            instance_of=self,
            settings=self._self_settings,
        )
        return self.__enforcer__

    def __getitem__(self, param):
        """
        Wraps a normal typed Generic in another proxy and applies enforcers for generics on it
        """
        return GenericProxy(self.__wrapped__.__getitem__(param))

    def __repr__(self):
        # if self.__wrapped__.__origin__ is None:
        #     return super().__repr__()
        r = super().__repr__()
        constraints = repr(self.__wrapped__.__args__)
        return r + "[{}]".format(constraints)


def get_enforcer(
    func: typing.Callable,
    generic: bool = False,
    settings=None,
    parent_root: typing.Optional[Validator] = None,
    instance_of: typing.Optional[GenericProxy] = None,
) -> Enforcer:
    """
    Adds an Enforcer instance to the passed function/generic if it doesn't yet exist
    or if it is not an instance of Enforcer

    Such instance is added as '__enforcer__'
    """
    if hasattr(func, "__enforcer__") and isinstance(func.__enforcer__, Enforcer):
        return getattr(func, "__enforcer__")
    else:
        # if not hasattr(func, '__enforcer__'):
        #    func = EnforceProxy(func)

        # if not isinstance(func.__enforcer__, Enforcer):
        # Replaces 'incorrect' enforcers
        enforcer = generate_new_enforcer(
            func, generic, parent_root, instance_of, settings
        )
        enforcer.reference = func
        try:
            setattr(func, "__enforcer__", enforcer)
        except AttributeError:
            pass

        return enforcer


def generate_new_enforcer(func, generic, parent_root, instance_of, settings):
    """
    Private function for generating new Enforcer instances for the incoming function
    """
    signature = None
    if parent_root is not None:
        if type(parent_root) is not Validator:
            raise TypeError("Parent validator must be a Validator")

    if instance_of is not None:
        if type(instance_of) is not GenericProxy:
            raise TypeError(
                "Instance of a generic must be derived from a valid Generic Proxy"
            )

    if generic:
        hints = OrderedDict()

        if instance_of:
            func = instance_of

        func_type = type(func)

        has_origin = func.__origin__ is not None

        # Collects generic's parameters - TypeVar-s specified on itself or on origin (if constrained)
        if not func.__parameters__ and (
            not has_origin or not func.__origin__.__parameters__
        ):
            raise TypeError("User defined generic is invalid")

        parameters = (
            func.__parameters__
            if func.__parameters__
            else func.__origin__.__parameters__
        )

        # Maps parameter names to parameters, while preserving the order of their definition
        for param in parameters:
            hints[param.__name__] = EnhancedTypeVar(param.__name__, type_var=param)

        # Verifies that constraints do not contradict generic's parameter definition
        # and bounds parameters to constraints (if constrained)
        bound = func.__args__ is not None
        if bound:
            for i, param in enumerate(hints.values()):
                arg = func.__args__[i]
                if is_type_of_type(arg, param):
                    param.__bound__ = arg
                else:
                    raise TypeError(
                        "User defined generic does not accept provided constraints"
                    )

        # NOTE:
        # Signature in generics should always point to the original unconstrained generic
        # This applies even to the instances of such Generics
        if has_origin:
            signature = func.__origin__
        else:
            signature = func.__wrapped__ if func_type is GenericProxy else func

        validator = init_validator(settings, hints, parent_root)
    else:
        func = inspect.unwrap(func)
        func_type = type(func)

        try:
            signature = inspect.signature(func)
            a = func.__annotations__
            hints = getattr(func, "__annotations__", {})
        except TypeError:
            if hasattr(func, "__call__") and inspect.ismethod(func.__call__):
                call = func.__call__
                signature = inspect.signature(call)
                # hints = typing.get_type_hints(call)
                hints = getattr(call, "__annotations__", {})
            elif hasattr(func, "__annotations__"):
                hints = getattr(func, "__annotations__")
            else:
                hints = {}
            # else:
            #     mutable = hasattr(func, "__dict__")
            #     message = "mutable" if mutable else "immutable"
            #     raise TypeError(
            #         "Oops, cannot apply enforcer to the {0} object".format(message)
            #     )

        bound = False
        validator = init_validator(settings, hints, parent_root)


    if hasattr(func, "__name__"):
        name = func.__name__
    elif hasattr(func, "__class__"):
        name = func.__class__.__name__
    else:
        raise NameError("No way known to derive name")

    if signature is None:
        if hasattr(func, "__add__"):
            signature = inspect.signature(func.__add__.__call__)
        else:
            raise TypeError("No way known to find signature")

    return Enforcer(name, validator, signature, hints, generic, bound, settings)


def process_errors(config, errors, hints, is_return_type=False):
    parser = config.errors.parser
    processor = config.errors.processor
    exception = config.errors.exception

    processor(parser, exception, errors, hints, is_return_type)


def generate_callable_from_signature(signature):
    """
    Generates a type from a signature of Callable object
    """
    # TODO: (*args, **kwargs) should result in Ellipsis (...) as a parameter
    any_positional = False
    any_keyword = False
    positional_arguments = []

    for param in signature.parameters.values():
        if param.kind == param.VAR_KEYWORD:
            any_keyword = True

        if not param.kind == param.KEYWORD_ONLY and not param.kind == param.VAR_KEYWORD:

            if param.kind == param.VAR_POSITIONAL:
                any_positional = True
            else:
                if param.annotation is inspect._empty:
                    positional_arguments.append(typing.Any)
                else:
                    positional_arguments.append(param.annotation)

    return_type = signature.return_annotation
    if return_type is inspect._empty:
        return_type = typing.Any

    if any_positional and len(positional_arguments) == 0:
        positional_arguments = ...
        if return_type == typing.Any:
            return typing.Callable

    return typing.Callable[positional_arguments, return_type]
