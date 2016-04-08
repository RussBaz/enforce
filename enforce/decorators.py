import sys
import inspect
from functools import wraps
import typing
from typing import get_type_hints, Callable, Any

from .exceptions import RuntimeTypeError


def check_iterability(vartype: typing.TypeVar, hint: typing.TypeVar):
    check_iterable = issubclass(vartype, typing.Iterable)
    check_not_str  = not issubclass(vartype, str)
    check_not_Any  = hint != typing.Any
    return check_iterable and check_not_str and check_not_Any


def check_recursive_types(types: typing.Iterable[typing.Tuple[str, typing.Any, typing.Any]]) -> typing.Tuple[bool, str]:
    """
    Recursively checks types of some iterable.

    Note, we don't count strings as iterable types
    (possible up for debate? can't think of a situation where you'd want to recurse on str types)

    Note, this is a /huge/ slowdown for large arrays. Possibly optimizations definitely exist.
    If it's ultra nested, yer gonna have a bad time.
    """
    error_message = "Argument '{0}' ('{1}') was not of type {2}. Actual type was {3}.\n"
    typecheck = True
    exception_text = ''
    for name, variable, hint in types:
        vartype = type(variable)
        isiterable = check_iterability(vartype, hint)
        if not issubclass(vartype, hint):
            typecheck = False
            exception_text += error_message.format(name, str(variable), hint, vartype)
        if isiterable:
            # If we're currently examining an iterable type we need to recurse
            # __tuple_params__ defined on line 646 of typing.py
            # Otherwise, types inherit from GenericMeta (line 878)
            if issubclass(hint, typing.Tuple):   # Tuples have their own parameter for some reason
                subhints = hint.__tuple_params__
            else:
                subhints = hint.__parameters__
            names = [name] * len(variable)   # also need to have name in there for error message
            if issubclass(type(variable), dict):
                # If we're looking at dict, need to check keys and items independently
                subhints1 = [subhints[0]] * len(variable)
                subhints2 = [subhints[1]] * len(variable)
                new_typecheck1, new_exception_text1 = check_recursive_types(zip(names, variable.keys(), subhints1))
                new_typecheck2, new_exception_text2 = check_recursive_types(zip(names, variable.values(), subhints2))
                new_typecheck      = new_typecheck1 and new_typecheck2
                new_exception_text = new_exception_text1 + new_exception_text2
            else:
                if len(subhints) == 1:    # If only 1 subhint then /possibly/ applies to all elements
                    subhints = [subhints] * len(variable)
                new_typecheck, new_exception_text = check_recursive_types(zip(names, variable, subhints))
            typecheck &= new_typecheck
            exception_text += new_exception_text

    return typecheck, exception_text


def runtime_validation(func: Callable) -> Callable:
    """
    This decorator enforces runtime parameter and return value validation
    It uses the standard Python 3.5 syntax for type hinting declaration and its validation
    """
    return_error_message = "Return value '{0}' was not of type {1}. Actual type was {2}."

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        This function will be returned by the decorator. It adds type checking before triggering
        the original function and then it checks for the output type. Only then it returns the
        output of original function.

        Note on expected behavior: If type is not specified, we assume that it's None.
        """
        # Setup initial types/hinting
        binded_arguments = inspect.signature(func).bind(*args, **kwargs)

        argument_hints = get_type_hints(func)
        return_hint = argument_hints.pop('return', type(None))

        if return_hint is None:
            return_hint = type(None)

        # check argument types
        types = [(name, binded_arguments.arguments.get(name), hint)
                 for name, hint in argument_hints.items()]
        typecheck, exception_text = (check_recursive_types(types))

        if not typecheck:
            exception_text = exception_text[:-1]
            raise RuntimeTypeError(exception_text)

        # check return type
        result = func(*args, **kwargs)
        return_type = type(result)

        if not issubclass(return_type, return_hint):
            raise RuntimeTypeError(return_error_message.format(str(result), return_hint, return_type))

        # If all checks pass, return result of func
        return result

    return wrapper
