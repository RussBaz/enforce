import inspect
import typing
from inspect import ismethoddescriptor
from functools import wraps
from pprint import pprint

from wrapt import decorator

from .exceptions import RuntimeTypeError
from .parsers import Parser
from .validators import Validator


def runtime_validation(data):
    """
    This decorator enforces runtime parameter and return value validation
    It uses the standard Python 3.5 syntax for type hinting declaration
    """

    @decorator
    def build_wrapper(wrapped, instance, args, kwargs):
        if instance is None:
            if inspect.isclass(wrapped):
                # Decorator was applied to a class
                for attr_name in dir(data):
                    try:
                        if attr_name == '__class__':
                            raise AttributeError
                        old_attr = getattr(data, attr_name)
                        new_attr = decorate(old_attr, None)
                        setattr(data, attr_name, new_attr)
                    except AttributeError:
                        pass
                return data
            else:
                # Decorator was applied to a function or staticmethod.
                if issubclass(type(data), staticmethod):
                    return staticmethod(decorate(data.__func__, None))
                return decorate(data, None)
        else:
            if inspect.isclass(instance):
                # Decorator was applied to a classmethod.
                print('class method')
                return decorate(data, None)
            else:
                # Decorator was applied to an instancemethod.
                print('instance method')
                return decorate(data, instance)

    generate_decorated = build_wrapper(data)
    return generate_decorated()

def decorate(data, obj_instance=None) -> typing.Callable:
    """
    Performs the function decoration
    """
    if not hasattr(data, '__annotations__'):
        return data

    func_signature = inspect.signature(data)

    argument_hints = typing.get_type_hints(data)

    validator = get_validator(data, argument_hints, obj_instance)

    if not validator:
        return data

    @decorator
    def universal(wrapped, instance, args, kwargs):
        """
        This function will be returned by the decorator. It adds type checking before triggering
        the original function and then it checks for the output type. Only then it returns the
        output of original function.
        """
        # In order to avoid problems with TypeVar-s, validator must be reset
        validator.reset()

        instance_method = False
        if instance is not None and not inspect.isclass(instance):
            instance_method = True

        if instance_method:
            binded_arguments = func_signature.bind(instance, *args, **kwargs)
        else:
            binded_arguments = func_signature.bind(*args, **kwargs)

        binded_arguments.apply_defaults()

        for name in argument_hints.keys():
            if name != 'return':
                argument = binded_arguments.arguments.get(name)
                if not validator.validate(argument, name):
                    break
                binded_arguments.arguments[name] = validator.data_out[name]
        else:
            _args = binded_arguments.args
            _kwargs = binded_arguments.kwargs
            if instance_method:
                if len(_args) > 1:
                    _args = _args[1:]
                else:
                    _args = tuple()
            result = wrapped(*_args, **_kwargs)
            if 'return' in argument_hints.keys():
                if not validator.validate(result, 'return'):
                    exception_text = parse_errors(validator.errors, argument_hints, True)
                    raise RuntimeTypeError(exception_text)
            return result

        exception_text = parse_errors(validator.errors, argument_hints)
        raise RuntimeTypeError(exception_text)

    return universal(data)


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
