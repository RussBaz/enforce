import sys
import inspect
from functools import wraps
from typing import get_type_hints, Callable, Any

from .exceptions import RuntimeTypeError
from .validators import Validator
from .parser import Parser


def runtime_validation(func: Callable) -> Callable:
    """
    This decorator enforces runtime parameter and return value validation
    It uses the standard Python 3.5 syntax for type hinting declaration
    """
    func_signature = inspect.signature(func)

    argument_hints = get_type_hints(func)

    parser = Parser()
    for name, hint in argument_hints.items():
        if hint is None:
            hint = type(None)
        parser.parse(hint, name)

    validator = parser.validator

    def parse_errors(errors, hints, return_type=False):
        """
        Generates an exception message based on which fields failed
        """
        error_message = "       Argument '{0}' was not of type {1}."
        return_error_message = "        Return value was not of type {0}."
        output = '\n  The following runtime type errors were encountered:'

        for error in errors:
            hint = hints.get(error, type(None))
            if hint is None:
                hint = type(None)
            if return_type:
                output += '\n' + return_error_message.format(hint)
            else:
                output +='\n' +  error_message.format(error, hint)
        return output

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        This function will be returned by the decorator. It adds type checking before triggering
        the original function and then it checks for the output type. Only then it returns the
        output of original function.
        """
        # In order to avoid problems with TypeVar-s, validator must be reset
        validator.reset()

        binded_arguments = func_signature.bind(*args, **kwargs)
        binded_arguments.apply_defaults()
        
        for name in argument_hints.keys():
            if name != 'return':
                argument = binded_arguments.arguments.get(name)
                if not validator.validate(argument, name):
                    break
                binded_arguments.arguments[name] = validator.data_out[name]
        else:
            result = func(*binded_arguments.args, **binded_arguments.kwargs)
            if 'return' in argument_hints.keys():
                if not validator.validate(result, 'return'):
                    exception_text = parse_errors(validator.errors, argument_hints, True)
                    raise RuntimeTypeError(exception_text)
            return result

        exception_text = parse_errors(validator.errors, argument_hints)
        raise RuntimeTypeError(exception_text)

    return wrapper
