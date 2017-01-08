import typing
import inspect
from collections import namedtuple, OrderedDict

from wrapt import ObjectProxy

from .types import EnhancedTypeVar, is_type_of_type
from .wrappers import Proxy, EnforceProxy
from .exceptions import RuntimeTypeError
from .validator import init_validator, Validator


# This TypeVar is used to indicate that he result of output validation
# is the same as the input to the output validation
T = typing.TypeVar('T')

# Convenience type for storing all incoming arguments in a single container
Parameters = namedtuple('Parameters', ['args', 'kwargs', 'skip'])


class Enforcer:
    """
    A container for storing type checking logic of functions
    """
    def __init__(self, validator, signature, hints, generic=False, bound=False, settings=None):
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

        if hasattr(self.reference, '__no_type_check__'):
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

        binded_arguments = self.signature.bind(*args, **kwargs)
        binded_arguments.apply_defaults()

        for name in self.hints.keys():
            # First, check argument types (every key not labeled 'return')
            if name != 'return':
                argument = binded_arguments.arguments.get(name)
                if not self.validator.validate(argument, name):
                    break
                binded_arguments.arguments[name] = self.validator.data_out[name]
        else:
            valdated_data = Parameters(binded_arguments.args, binded_arguments.kwargs, skip)
            return valdated_data

        exception_text = parse_errors(self.validator.errors, self.hints)
        raise RuntimeTypeError(exception_text)

    def validate_outputs(self, output_data: T) -> T:
        """
        Calls a validator on a function return value
        """
        if self.settings is not None and not self.settings.enabled:
            return output_data

        if 'return' in self.hints.keys():
            if not self.validator.validate(output_data, 'return'):
                exception_text = parse_errors(self.validator.errors, self.hints, True)
                raise RuntimeTypeError(exception_text)
            else:
                return self.validator.data_out['return']
        else:
            return output_data

    def reset(self):
        """
        Clears validator internal state
        """
        self.validator.reset()


class GenericProxy(ObjectProxy):
    """
    A proxy object for typing.Generics user defined subclasses which always returns proxied objects
    """
    __enforcer__ = None

    def __init__(self, wrapped):
        """
        Creates an enforcer instance on a just wrapped user defined Generic
        """
        wrapped_type = type(wrapped)

        if is_type_of_type(wrapped_type, GenericProxy):
            super().__init__(wrapped.__wrapped__)
            apply_enforcer(self, generic=True, instance_of=self)
        elif is_type_of_type(wrapped_type, typing.GenericMeta):
            super().__init__(wrapped)
            apply_enforcer(self, generic=True)
        else:
            raise TypeError('Only generics can be wrapped in GenericProxy')

    def __call__(self, *args, **kwargs):
        return apply_enforcer(self.__wrapped__(*args, **kwargs), generic=True, instance_of=self)

    def __getitem__(self, param):
        """
        Wraps a normal typed Generic in another proxy and applies enforcers for generics on it
        """
        return GenericProxy(self.__wrapped__.__getitem__(param))


def apply_enforcer(func: typing.Callable,
                   generic: bool=False,
                   settings = None,
                   parent_root: typing.Optional[Validator]=None,
                   instance_of: typing.Optional[GenericProxy]=None) -> typing.Callable:
    """
    Adds an Enforcer instance to the passed function/generic if it doesn't yet exist
    or if it is not an instance of Enforcer

    Such instance is added as '__enforcer__'
    """
    if not hasattr(func, '__enforcer__') or not isinstance(func.__enforcer__, Enforcer):
    #if not hasattr(func, '__enforcer__'):
    #    func = EnforceProxy(func)

    #if not isinstance(func.__enforcer__, Enforcer):
        # Replaces 'incorrect' enforcers
        func.__enforcer__ = generate_new_enforcer(func, generic, parent_root, instance_of, settings)
        func.__enforcer__.reference = func

    return func


def generate_new_enforcer(func, generic, parent_root, instance_of, settings):
    """
    Private function for generating new Enforcer instances for the incoming function
    """
    if parent_root is not None:
        if type(parent_root) is not Validator:
            raise TypeError('Parent validator must be a Validator')

    if instance_of is not None:
        if type(instance_of) is not GenericProxy:
            raise TypeError('Instance of a generic must be derived from a valid Generic Proxy')

    if generic:
        hints = OrderedDict()

        if instance_of:
            func = instance_of

        func_type = type(func)

        has_origin = func.__origin__ is not None

        # Collects generic's parameters - TypeVar-s specified on itself or on origin (if constrained)
        if not func.__parameters__ and (not has_origin or not func.__origin__.__parameters__):
            raise TypeError('User defined generic is invalid')

        parameters = func.__parameters__ if func.__parameters__ else func.__origin__.__parameters__

        # Maps parameter names to parameters, while preserving the order of their definition
        for param in parameters:
            hints[param.__name__] = EnhancedTypeVar(param.__name__, type_var=param)

        # Verifies that constraints do not contradict generic's parameter definition
        # and bounds parameters to constraints (if constrained)
        bound = bool(func.__args__)
        if bound:
            for i, param in enumerate(hints.values()):
                arg = func.__args__[i]
                if is_type_of_type(arg, param):
                    param.__bound__ = arg
                else:
                    raise TypeError('User defined generic does not accept provided constraints')

        # NOTE:
        # Signature in generics should always point to the original unconstrained generic
        # This applies even to the instances of such Generics

        if has_origin:
            signature = func.__origin__
        else:
            signature = func.__wrapped__ if func_type is GenericProxy else func

        validator = init_validator(hints, parent_root)
    else:
        if type(func) is Proxy:
            signature = inspect.signature(func.__wrapped__)
            hints = typing.get_type_hints(func.__wrapped__)
        else:
            signature = inspect.signature(func)
            hints = typing.get_type_hints(func)

        bound = False
        validator = init_validator(hints, parent_root)

    return Enforcer(validator, signature, hints, generic, bound, settings)


def parse_errors(errors: typing.List[str], hints:typing.Dict[str, type], return_type: bool=False) -> str:
    """
    Generates an exception message based on which fields failed
    """
    error_message = "       Argument '{0}' was not of type {1}. Actual type was {2}."
    return_error_message = "        Return value was not of type {0}. Actual type was {1}."
    output = "\n  The following runtime type errors were encountered:"

    for error in errors:
        argument_name, argument_type = error
        hint = hints.get(argument_name, type(None))
        if hint is None:
            hint = type(None)
        if return_type:
            output += '\n' + return_error_message.format(hint, argument_type)
        else:
            output += '\n' +  error_message.format(argument_name, hint, argument_type)
    return output


def generate_callable_from_signature(signature):
    """
    Generates a type from a signature of Callable object
    """
    # TODO: (*args, **kwargs) should result in Ellipsis (...) as a parameter
    result = typing.Callable
    any_positional = False
    positional_arguments = []

    for param in signature.parameters.values():
        if param.kind == param.KEYWORD_ONLY or param.kind == param.VAR_KEYWORD:
            break

        if param.kind == param.VAR_POSITIONAL:
            any_positional = True

        if param.annotation is inspect._empty:
            positional_arguments.append(typing.Any)
        else:
            positional_arguments.append(param.annotation)
    else:
        return_type = signature.return_annotation
        if return_type is inspect._empty:
            return_type = typing.Any

        if any_positional and all([a == typing.Any for a in positional_arguments]):
            positional_arguments = ...
            if return_type != typing.Any:
                result = typing.Callable[positional_arguments, return_type]
        elif (len(positional_arguments) == 0 or
            any([a != typing.Any for a in positional_arguments]) or
            return_type is not typing.Any):
            result = typing.Callable[positional_arguments, return_type]

    return result
