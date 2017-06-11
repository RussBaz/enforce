import inspect
import typing
import functools
from multiprocessing import RLock
from functools import wraps

from wrapt import decorator, ObjectProxy

from .settings import Settings
#from .wrappers import Proxy
from .enforcers import apply_enforcer, Parameters, GenericProxy
from .types import is_type_of_type


BuildLock = RLock()
RunLock = RLock()


def runtime_validation(data=None, *, enabled=None, group=None):
    """
    This decorator enforces runtime parameter and return value type checking validation
    It uses the standard Python 3.5 syntax for type hinting declaration
    """
    with RunLock:
        if enabled is not None and not isinstance(enabled, bool):
            raise TypeError('Enabled parameter must be boolean')

        if group is not None and not isinstance(group, str):
            raise TypeError('Group parameter must be string')

        if enabled is None and group is None:
            enabled = True

        # see https://wrapt.readthedocs.io/en/latest/decorators.html#decorators-with-optional-arguments
        if data is None:
            return functools.partial(runtime_validation, enabled=enabled, group=group)

        configuration = Settings(enabled=enabled, group=group)

        # ????
        if data.__class__ is type and is_type_of_type(data, tuple, covariant=True):
            try:
                fields = data._fields
                field_types = data._field_types

                return get_typed_namedtuple(configuration, data, fields, field_types)

            except AttributeError:
                pass

        build_wrapper = get_wrapper_builder(configuration)

        if data.__class__ is property:
            generate_decorated = build_wrapper(data.fset)
            return data.setter(generate_decorated())

        generate_decorated = build_wrapper(data)
        return generate_decorated()


def decorate(data, configuration, obj_instance=None, parent_root=None) -> typing.Callable:
    """
    Performs the function decoration with a type checking wrapper

    Works only if '__annotations__' are defined on the passed object
    """
    if not hasattr(data, '__annotations__'):
        return data

    data = apply_enforcer(data, parent_root=parent_root, settings=configuration)

    universal = get_universal_decorator()

    return universal(data)


def get_universal_decorator():
    def universal(wrapped, instance, args, kwargs):
        """
        This function will be returned by the decorator. It adds type checking before triggering
        the original function and then it checks for the output type. Only then it returns the
        output of original function.
        """
        with RunLock:
            enforcer = wrapped.__enforcer__
            skip = False

            # In order to avoid problems with TypeVar-s, validator must be reset
            enforcer.reset()

            instance_method = False
            if instance is not None and not inspect.isclass(instance):
                instance_method = True

            if hasattr(wrapped, '__no_type_check__'):
                skip = True

            if instance_method:
                parameters = Parameters([instance, *args], kwargs, skip)
            else:
                parameters = Parameters(args, kwargs, skip)

            # First, check argument types (every key not labelled 'return')
            _args, _kwargs, _ = enforcer.validate_inputs(parameters)

            if instance_method:
                if len(_args) > 1:
                    _args = _args[1:]
                else:
                    _args = tuple()

            result = wrapped(*_args, **_kwargs)

            # we *only* return result if all type checks passed
            if skip:
                return result
            else:
                return enforcer.validate_outputs(result)

    return decorator(universal)


def get_wrapper_builder(configuration, excluded_fields=None):
    if excluded_fields is None:
        excluded_fields = set()

    excluded_fields |= {'__class__', '__new__'}

    def build_wrapper(wrapped, instance, args, kwargs):
        if instance is None:
            if inspect.isclass(wrapped):
                # Decorator was applied to a class
                root = None
                if is_type_of_type(wrapped, typing.Generic, covariant=True):
                    wrapped = GenericProxy(wrapped)
                    root = wrapped.__enforcer__.validator

                for attr_name in dir(wrapped):
                    try:
                        if attr_name in excluded_fields:
                            raise AttributeError
                        old_attr = getattr(wrapped, attr_name)

                        if old_attr.__class__ is property:
                            old_fset = old_attr.fset
                            new_fset = decorate(old_fset, configuration, obj_instance=None, parent_root=root)
                            new_attr = old_attr.setter(new_fset)
                        else:
                            new_attr = decorate(old_attr, configuration, obj_instance=None, parent_root=root)
                        setattr(wrapped, attr_name, new_attr)
                    except AttributeError:
                        pass
                return wrapped
            else:
                # Decorator was applied to a function or staticmethod.
                if issubclass(type(wrapped), staticmethod):
                    return staticmethod(decorate(wrapped.__func__, configuration, None))
                return decorate(wrapped, configuration, None)
        else:
            if inspect.isclass(instance):
                # Decorator was applied to a classmethod.
                return decorate(wrapped, configuration, None)
            else:
                # Decorator was applied to an instancemethod.
                return decorate(wrapped, configuration, instance)

    return decorator(build_wrapper)


def get_typed_namedtuple(configuration, typed_namedtuple, fields, fields_types):
    args = ''.join(field + ': ' + (fields_types.get(field, any)).__name__ + ',' for field in fields)
    args = args[:-1]

    context = {}

    new_init_template = """def init_data({args}): return locals()"""

    new_init_template = new_init_template.format(args=args)

    exec(new_init_template, context)

    init_data = context['init_data']

    init_data = decorate(init_data, configuration)

    class NamedTupleProxy(ObjectProxy):
        def __call__(self, *args, **kwargs):
            data = init_data(*args, **kwargs)
            return self.__wrapped__(**data)

    return NamedTupleProxy(typed_namedtuple)
