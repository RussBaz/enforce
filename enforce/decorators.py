import inspect
import typing
from functools import wraps

from .exceptions import RuntimeTypeError
from .parsers import Parser
from .validators import Validator


def runtime_validation(data, origin=True):
    """
    This decorator enforces runtime parameter and return value validation
    It uses the standard Python 3.5 syntax for type hinting declaration
    """

    if isinstance(data, type):
        for attr_name in dir(data):
            try:
                if attr_name == '__class__':
                    raise AttributeError
                old_attr = getattr(data, attr_name)
                new_attr = decorate(old_attr)
                setattr(data, attr_name, new_attr)
            except AttributeError:
                pass
    else:
        data = decorate(data)
    return data


def decorate(data):
    """
    Performs the function decoration
    """
    if not hasattr(data, '__annotations__'):
        return data

    func_signature = inspect.signature(data)

    argument_hints = typing.get_type_hints(data)

    validator = get_validator(data, argument_hints)

    if not validator:
        return data

    @wraps(data)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
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
            result = data(*binded_arguments.args, **binded_arguments.kwargs)
            if 'return' in argument_hints.keys():
                if not validator.validate(result, 'return'):
                    exception_text = parse_errors(validator.errors, argument_hints, True)
                    raise RuntimeTypeError(exception_text)
            return result

        exception_text = parse_errors(validator.errors, argument_hints)
        raise RuntimeTypeError(exception_text)

    return wrapper


def get_validator(func: typing.Callable, hints: typing.Dict):
    """
    Checks if the function was already decorated with a type checker
    Returns new validator if it was not and creates a new attribute in the passed function
    with a new validator.
    Otherwise, returns None
    """
    try:
        if isinstance(func.__validator__, Validator):
            return None
        else:
            func.__validator__ = init_validator(hints)
            return func.__validator__
    except AttributeError:
        func.__validator__ = init_validator(hints)
        return func.__validator__


def init_validator(hints: typing.Dict):
    """
    Returns a new validator instance from a given dictionary of type hints
    """
    parser = Parser()
    for name, hint in hints.items():
        if hint is None:
            hint = type(None)
        parser.parse(hint, name)

    return parser.validator


def parse_errors(errors, hints, return_type=False):
    """
    Generates an exception message based on which fields failed
    """
    error_message = "       Argument '{0}' was not of type {1}. Actual type was: {2}"
    return_error_message = "        Return value was not of type {0}. Actual type was: {1}"
    output = '\n  The following runtime type errors were encountered:'

    for error in errors:
        hint = hints.get(error, type(None))
        if hint is None:
            hint = type(None)
        if return_type:
            output += '\n' + return_error_message.format(hint, 'mmm')
        else:
            output += '\n' +  error_message.format(error, hint, 'eeee')
    return output
