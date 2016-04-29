import inspect
import typing
from inspect import ismethoddescriptor
from functools import wraps
from pprint import pprint

from wrapt import decorator

from .exceptions import RuntimeTypeError
from .parsers import Parser
from .validators import Validator
from .enforcers import apply_enforcer, Parameters


def runtime_validation(data):
    """
    This decorator enforces runtime parameter and return value type checking validation
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
    Performs the function decoration with a type checking wrapper

    Works only if '__annotations__' are defined on the passed object
    """
    if not hasattr(data, '__annotations__'):
        return data

    apply_enforcer(data)

    @decorator
    def universal(wrapped, instance, args, kwargs):
        """
        This function will be returned by the decorator. It adds type checking before triggering
        the original function and then it checks for the output type. Only then it returns the
        output of original function.
        """
        enforcer = data.__enforcer__

        # In order to avoid problems with TypeVar-s, validator must be reset
        enforcer.reset()

        instance_method = False
        if instance is not None and not inspect.isclass(instance):
            instance_method = True

        if instance_method:
            parameters = Parameters([instance, *args], kwargs)
        else:
            parameters = Parameters(args, kwargs)

        # First, check argument types (every key not labelled 'return')
        _args, _kwargs = enforcer.validate_inputs(parameters)

        if instance_method:
            if len(_args) > 1:
                _args = _args[1:]
            else:
                _args = tuple()

        result = wrapped(*_args, **_kwargs)

        # we *only* return result if all type checks passed
        return enforcer.validate_outputs(result)

    return universal(data)
