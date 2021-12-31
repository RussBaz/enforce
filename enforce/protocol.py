from typing import (
    Optional,
    List,
    Dict,
    Union,
    Any,
    Callable,
    get_type_hints,
)

from . import domain_types as dt
from .assertions import get_assert_for

__protocol_registry = {}  # type: dt.ProtocolRegistry


def register(
    data: Optional[Any],
    *,
    name: Optional[dt.ProtocolId] = None,
    requires: Optional[dt.Fields] = None,
    ignores: Optional[List[dt.FieldName]] = None
) -> dt.ProtocolDefinition:
    ignored_fields = {
        "__abstractmethods__",
        "__annotations__",
        "__protocol_name__",
        "__protocol_extra_check__",
        "__weakref__",
        "_is_protocol",
        "_gorg",
        "__dict__",
        "__args__",
        "__slots__",
        "_get_protocol_attrs",
        "__next_in_mro__",
        "__parameters__",
        "__origin__",
        "__orig_bases__",
        "__extra__",
        "__tree_hash__",
        "__module__",
    }

    def is_ignored_field(s: str):
        if s.startswith("_abc_"):
            return True

        if s in ignored_fields:
            return True

        return False

    if data is None and name is None:
        raise TypeError("No Protocol was given")
    else:
        if name:
            protocol_name = name
        else:
            protocol_name = data.__protocol_name__

    own_code_annotations = {}  # type: Dict[dt.FieldName, dt.FieldDefinition]

    try:
        own_code_annotations = dict(data.__annotations__)
    except AttributeError:
        pass

    if len(protocol_name) < 1:
        raise TypeError("Invalid protocol name - an empty string")

    if protocol_name in __protocol_registry:
        raise TypeError("Protocol is already registered: {}".format(protocol_name))

    tmp_protocol_definition = {}  # type: Dict[dt.FieldName, dt.FieldDefinition]

    extra_tests = None

    if data is not None:
        try:
            extra_tests = data.__protocol_extra_check__
        except AttributeError:
            pass

        field_names_to_process = own_code_annotations.keys() | set(dir(data))
        for field_name in field_names_to_process:
            if not is_ignored_field(field_name):
                hint = None  # type: Optional[dt.FieldDefinition]
                hints = {}  # type: Dict[dt.FieldName, dt.FieldDefinition]

                try:
                    field = getattr(data, field_name)
                    hints = get_type_hints(field)
                except (TypeError, AttributeError):
                    hint = own_code_annotations.get(field_name, None)
                    is_callable = isinstance(hint, Callable)
                else:
                    is_callable = hasattr(field, "__call__")

                if is_callable and hint is None:
                    if len(hints) < 1:
                        hint = Callable
                    else:
                        returns = hints.get("return", Any)
                        inputs = [v for k, v in hints.items() if k != "return"]

                        hint = Callable[inputs, returns]

                if hint is None:
                    hint = Any

                tmp_protocol_definition[field_name] = hint

    if requires is not None:
        for field_name, field in requires.items():
            if not is_ignored_field(field_name):
                tmp_protocol_definition[field_name] = field

    if ignores is not None:
        for field_name in ignores:
            try:
                del tmp_protocol_definition[field_name]
            except KeyError:
                pass

    protocol_definition = dt.ProtocolDefinition(
        id=protocol_name,
        fields={k: get_assert_for(v) for k, v in tmp_protocol_definition.items()},
        extra_tests=extra_tests,
    )

    __protocol_registry[protocol_name] = protocol_definition

    return protocol_definition


def is_registered(protocol_id: Union[dt.ProtocolId, type]) -> bool:
    if not isinstance(protocol_id, dt.ProtocolId.__supertype__):
        protocol_id = protocol_id.__protocol_name__

    return protocol_id in __protocol_registry


def retrieve(protocol_id: dt.ProtocolId) -> Optional[dt.ProtocolDefinition]:
    return __protocol_registry.get(protocol_id, None)


def deregister_all(do_it=False):
    if do_it:
        __protocol_registry.clear()


def verify_protocol(protocol: dt.ProtocolDefinition, data: Any) -> bool:
    pass


class _Protocol(object):
    __slots__ = ()

    def __getitem__(self, data: Union[dt.ProtocolId, type]) -> dt.ProtocolDefinition:
        if not is_registered(data):
            raise TypeError("Not a valid Protocol: {!s}".format(data))
        return retrieve(data)


P = _Protocol()
