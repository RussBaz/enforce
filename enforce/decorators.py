import sys
import inspect
from functools import wraps
from typing import get_type_hints, Callable, Any

from .exceptions import RuntimeTypeError


def runtime_validation(func: Callable) -> Callable:
    """
    This decorator enforces runtime parameter and return value validation
    It uses the standard Python 3.5 syntax for type hinting declaration and its validation
    """
    error_message = "Argument '{0}' ('{1}') was not of type {2}. Actual type was {3}."
    return_error_message = "Return value '{0}' was not of type {1}. Actual type was {2}."

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        This function will be returned by the decorator. It adds type checking before triggering
        the original function and then it checks for the output type. Only then it returns the
        output of original function.
        """
        exception_text = ''

        binded_arguments = inspect.signature(func).bind(*args, **kwargs)

        argument_hints = get_type_hints(func)
        return_hint = argument_hints.pop('return', type(None))

        if return_hint is None:
            return_hint = type(None)
        
        for name, hint in argument_hints.items():
            if hint is None:
                hint = type(None)
            argument = binded_arguments.arguments.get(name)
            argument_type = type(argument)
            if not issubclass(argument_type, hint):
                exception_text += error_message.format(name, str(argument), hint, argument_type) + '\n'

        if exception_text:
            exception_text = exception_text[:-1]
            raise RuntimeTypeError(exception_text)

        result = func(*args, **kwargs)
        return_type = type(result)

        if not issubclass(return_type, return_hint):
            raise RuntimeTypeError(return_error_message.format(str(result), return_hint, return_type))

        return result

    return wrapper
