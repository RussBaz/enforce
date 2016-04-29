import typing
import inspect
from collections import namedtuple

from .exceptions import RuntimeTypeError
from .parsers import Parser


# This TypeVar is used to indicate that he result of output validation
# is the same as the input to the output validation
T = typing.TypeVar('T')

# Convenience type for storing all incoming arguments in a single container
Parameters = namedtuple('Parameters', ['args', 'kwargs'])

class Enforcer:
    """
    A container for storing type checking logic of functions
    """
    def __init__(self, validator, signature, hints, parent=None):
        self.validator = validator
        self.signature = signature
        self.hints = hints
        self.parent = parent

    def validate_inputs(self, input_data: Parameters) -> Parameters:
        """
        Calls a validator for each function argument
        """
        args = input_data.args
        kwargs = input_data.kwargs

        binded_arguments = self.signature.bind(*args, **kwargs)
        binded_arguments.apply_defaults()

        for name in self.hints.keys():
            # First, check argument types (every key not labelled 'return')
            if name != 'return':
                argument = binded_arguments.arguments.get(name)
                if not self.validator.validate(argument, name):
                    break
                binded_arguments.arguments[name] = self.validator.data_out[name]
        else:
            valdated_data = Parameters(binded_arguments.args, binded_arguments.kwargs)
            return valdated_data

        exception_text = parse_errors(self.validator.errors, self.hints)
        raise RuntimeTypeError(exception_text)

    def validate_outputs(self, output_data: T) -> T:
        """
        Calls a validator on a function return value
        """
        if 'return' in self.hints.keys():
            if not self.validator.validate(output_data, 'return'):
                exception_text = parse_errors(self.validator.errors, self.hints, True)
                raise RuntimeTypeError(exception_text)
            else:
                return self.validator.data_out['return']

    def reset(self):
        """
        Clears validator internal state
        """
        self.validator.reset()


def apply_enforcer(func: typing.Callable) -> typing.Callable:
    """
    Adds an Enforcer instance to the passed function if it doesn't yet exist
    or if it is not an instance of Enforcer

    Such instance is added as '__enforcer__'
    """
    def generate_new_enforcer():
        """
        Private function for generating new Enforcer instances for the incoming function
        """
        signature = inspect.signature(func)
        hints = typing.get_type_hints(func)
        validator = init_validator(hints)

        return Enforcer(validator, signature, hints)

    if not hasattr(func, '__enforcer__'):
        func.__enforcer__ = generate_new_enforcer()
    elif not isinstance(func.__enforcer__, Enforcer):
        func.__enforcer__ = generate_new_enforcer()

    return func


def init_validator(hints: typing.Dict) -> Parser:
    """
    Returns a new validator instance from a given dictionary of type hints
    """
    parser = Parser()
    for name, hint in hints.items():
        if hint is None:
            hint = type(None)
        parser.parse(hint, name)

    return parser.validator


def parse_errors(errors: typing.List[str], hints:typing.Dict[str, type], return_type: bool=False) -> str:
    """
    Generates an exception message based on which fields failed
    """
    error_message = "       Argument '{0}' was not of type {1}."
    return_error_message = "        Return value was not of type {0}."
    output = "\n  The following runtime type errors were encountered:"

    for error in errors:
        hint = hints.get(error, type(None))
        if hint is None:
            hint = type(None)
        if return_type:
            output += '\n' + return_error_message.format(hint)
        else:
            output += '\n' +  error_message.format(error, hint)
    return output
