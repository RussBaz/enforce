import inspect
import typing
from inspect import ismethoddescriptor
from functools import wraps
from pprint import pprint

from wrapt import decorator

from .exceptions import RuntimeTypeError
from .parsers import Parser
from .validators import Validator


def runtime_validation(data, instance=None):
    """
    This decorator enforces runtime parameter and return value validation
    It uses the standard Python 3.5 syntax for type hinting declaration
    """
    # If class, try to apply to every attribute
    if isinstance(data, type):
        for attr_name in dir(data):
            try:
                if attr_name == '__class__':
                    raise AttributeError
                old_attr = getattr(data, attr_name)
                new_attr = decorate(old_attr, instance)
                setattr(data, attr_name, new_attr)
            except AttributeError:
                pass
    elif isinstance(data, staticmethod):
        data = staticmethod(decorate(data.__func__))
    elif isinstance(data, classmethod):
        data = classmethod(decorate(data.__func__))
    else:
        data = decorate(data, instance)
    return data

    # Some experiments

    #@decorator
    #def universal(wrapped, instance, args, kwargs):
    #    if instance is None:
    #        if inspect.isclass(wrapped):
    #            # Decorator was applied to a class
    #            # Cycle trough attributes and replace functions with annotations
    #            for attr_name in dir(wrapped):
    #                try:
    #                    if attr_name == '__class__':
    #                        raise AttributeError
    #                    old_attr = getattr(wrapped, attr_name)
    #                    new_attr = decorate(old_attr, None)
    #                    setattr(wrapped, attr_name, new_attr)
    #                except AttributeError:
    #                    pass
    #            return wrapped
    #        else:
    #            # Decorator was applied to a function or staticmethod.
    #            return decorate(wrapped, None)
    #    else:
    #        if inspect.isclass(instance):
    #            # Decorator was applied to a classmethod.
    #            return wrapped(*args, **kwargs)
    #        else:
    #            # Decorator was applied to an instancemethod.
    #            return wrapped(*args, **kwargs)


def decorate(data, obj_instance=None):
    """
    Performs the function decoration
    """
    if not hasattr(data, '__annotations__'):
        return data

    func_signature = inspect.signature(data)

    # Argument hints is dict with str keys -> value types and 'return' -> type
    argument_hints = typing.get_type_hints(data)

    validator = get_validator(data, argument_hints, obj_instance)

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
            # First, check argument types (every key not labelled 'return')
            if name != 'return':
                argument = binded_arguments.arguments.get(name)
                if not validator.validate(argument, name):
                    break
                binded_arguments.arguments[name] = validator.data_out[name]
        else:
            # Second, check return types
            result = data(*binded_arguments.args, **binded_arguments.kwargs)
            if 'return' in argument_hints.keys():
                if not validator.validate(result, 'return'):
                    exception_text = parse_errors(validator.errors, argument_hints, True)
                    raise RuntimeTypeError(exception_text)
            return result

        exception_text = parse_errors(validator.errors, argument_hints)
        raise RuntimeTypeError(exception_text)

    return wrapper


def get_validator(func: typing.Callable, hints: typing.Dict, instance=None):
    """
    Checks if the function was already decorated with a type checker
    Returns new validator if it was not and creates a new attribute in the passed function
    with a new validator.
    Otherwise, returns None
    """
    if instance:
        func = instance
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
    # DEBUG
    print(str(parser))

    return parser.validator


def parse_errors(errors, hints, return_type=False):
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
