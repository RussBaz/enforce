import inspect
import typing
import functools
from collections import OrderedDict
from multiprocessing import RLock
from typing import _ForwardRef

from wrapt import decorator, ObjectProxy

from .settings import Settings
from .enforcers import apply_enforcer, Parameters, GenericProxy, process_errors
from .types import is_type_of_type
from .validator import init_validator


BuildLock = RLock()
RunLock = RLock()


def protocol_registration(data=None, *, name: typing.Optional[str]=None):
    """
    This decorator creates and registers a protocol based on a provided class
    """
    pass


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


def _should_decorate_later(data):
    for annotation_val in data.__annotations__.values():
        if not isinstance(annotation_val, str):
            continue
        # test if we can reference the class
        frame = inspect.stack()[5].frame
        try:
            typing._eval_type(_ForwardRef(annotation_val), frame.f_globals, frame.f_locals)
        except NameError:
            # this indicates that late binding is in order
            return True
    return False


def _decorate(data, configuration, obj_instance=None, parent_root=None, stack_depth=1) -> typing.Callable:
    data = apply_enforcer(data, parent_root=parent_root, settings=configuration)
    universal = get_universal_decorator(stack_depth=stack_depth)
    return universal(data)


def _decorate_later(data, configuration, obj_instance=None, parent_root=None) -> typing.Callable:
    enforced = None

    def wrap(*args, **kwargs):
        nonlocal enforced, data
        if enforced is None:
            enforced = _decorate(data, configuration, obj_instance, parent_root, stack_depth=2)
        return enforced(*args, **kwargs)

    return wrap


def decorate(data, configuration, obj_instance=None, parent_root=None) -> typing.Callable:
    """
    Performs the function decoration with a type checking wrapper

    Works only if '__annotations__' are defined on the passed object
    """
    if not hasattr(data, '__annotations__'):
        return data

    if _should_decorate_later(data):
        return _decorate_later(data, configuration, obj_instance, parent_root)
    else:
        return _decorate(data, configuration, obj_instance, parent_root)


def get_universal_decorator(stack_depth=1):
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

            frame = inspect.stack()[stack_depth].frame
            outer_locals = frame.f_locals
            outer_globals = frame.f_globals

            enforcer.set_outer_scope_variables(outer_locals, outer_globals)

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

    @decorator
    def build_wrapper(wrapped, instance, args, kwargs):
        if instance is None:
            if inspect.isclass(wrapped):
                # Decorator was applied to a class
                root = None
                if is_type_of_type(wrapped, typing.Generic, covariant=True):
                    wrapped = GenericProxy(wrapped, settings=configuration)
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
                        elif attr_name in wrapped.__dict__ and type(wrapped.__dict__[attr_name]) is staticmethod:
                            # if decorator was applied to class need to handle @staticmethods differently
                            new_attr = staticmethod(decorate(
                                old_attr,
                                configuration,
                                obj_instance=None,
                                parent_root=root
                            ))
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
                print('classmethod')
                return decorate(wrapped, configuration, None)
            else:
                # Decorator was applied to an instancemethod.
                print('instancemethod')
                print(type(wrapped))
                return decorate(wrapped, configuration, instance)

    return build_wrapper


def get_typed_namedtuple(configuration, typed_namedtuple, fields, fields_types):
    # in_fields is an artificial hints container
    in_fields = OrderedDict()
    for field in fields:
        in_fields[field] = fields_types.get(field, typing.Any)

    validator = init_validator(configuration, in_fields)

    tuple_name = typed_namedtuple.__name__

    class NamedTupleProxy(ObjectProxy):
        def __call__(self, *args, **kwargs):
            number_of_arguments = len(args) + len(kwargs)
            expected_number_of_arguments = len(in_fields)
            unknown_arguments = [str(key) for key in kwargs if key not in in_fields.keys()]

            if unknown_arguments:
                unexpected_names = ', '.join("'"+a+"'" for a in unknown_arguments)
                e = '{0}() got an unexpected keyword argument: {1}'
                e = e.format(tuple_name, unexpected_names)
                raise TypeError(e)

            if number_of_arguments < expected_number_of_arguments:
                missing_arguments = ["'"+str(arg)+"'" for arg in list(in_fields.keys())[number_of_arguments:] if arg not in kwargs]
                missing_names = ', '.join(missing_arguments)
                e = '{0}() missing {1} keyword arguments: {2}'
                e = e.format(tuple_name, len(missing_arguments), missing_names)
                raise TypeError(e)
            elif number_of_arguments > expected_number_of_arguments:
                e = '{0}() takes {1} positional arguments but {2} were given'
                e = e.format(tuple_name, expected_number_of_arguments, number_of_arguments)
                raise TypeError(e)

            in_fields_items = iter(in_fields.keys())
            in_data = OrderedDict()
            out_data = OrderedDict()

            for arg in args:
                key = next(in_fields_items)
                in_data[key] = arg

            if len(kwargs) > 0:
                for key, value in kwargs.items():
                    in_data[key] = value

            validator.reset()
            for key, value in in_data.items():
                validator.validate(value, key)
                out_data[key] = validator.data_out[key]

            errors = validator.errors

            if errors:
                process_errors(configuration, errors, in_fields)

            return self.__wrapped__(**out_data)

    return NamedTupleProxy(typed_namedtuple)
