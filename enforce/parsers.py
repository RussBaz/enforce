import typing
from collections import namedtuple

# This enables a support for Python version 3.5.0-3.5.2
try:
    from typing import UnionMeta
except ImportError:
    UnionMeta = typing.Union

from . import nodes
from .types import EnhancedTypeVar, is_named_tuple, is_wrapped_generic
from .protocol import _Protocol


ParserChoice = namedtuple('ParserChoice', ['validator', 'parser'])


def get_parser(node, hint, validator, parsers=None):
    """
    Yields a parser function for a given type hint
    """
    if parsers is None:
        parsers = TYPE_PARSERS

    hint_type = type(hint)

    if hint_type is str:
        parser = _parse_unwrapped_forward_ref
    elif hint_type == type:
        _fail_on_unacceptable_hint(node, hint, validator, parsers)
        parser = parsers.get(hint, _get_aliased_parser_or_default(hint, _parse_default))
    else:
        _fail_on_unacceptable_hint(node, hint_type, validator, parsers)
        parser = parsers.get(hint_type, _get_aliased_parser_or_default(hint, _parse_default))

    yield parser(node, hint, validator, parsers)


def _fail_on_unacceptable_hint(node, hints, validator, parsers):
    fail_with = TYPE_ERROR_GENERATORS.get(hints, None)
    if fail_with is not None:
        fail_with(node, hints, validator, parsers)


def _get_aliased_parser_or_default(hint, default):
    """
    After a normal parser selection fails,
    It will try running more complex parser selection suite
    before returning the most basic default parser

    It will go through the list in a definition order
    and tests each entry
    (calls 'validator' property with the int as a parameter)
    If any 'validator' returns True,
    Then this function returns the associated parser

    Otherwise, if all tests fail, it returns the default parser
    passed in as an argument
    """
    for choice in ALIASED_TYPE_PARSERS:
        if choice.validator(hint):
            return choice.parser

    return default


def _parse_namedtuple(node, hint, validator, parsers):
    new_node = yield nodes.NamedTupleNode(hint, validator.settings.errors.exception)
    validator.all_nodes.append(new_node)
    yield _yield_parsing_result(node, new_node)


def _parse_default(node, hint, validator, parsers):
    if str(hint).startswith('typing.Union'):
        yield _parse_union(node, hint, validator, parsers)
    else:
        new_node = yield nodes.SimpleNode(hint)
        validator.all_nodes.append(new_node)
        yield _yield_parsing_result(node, new_node)


def _parse_union(node, hint, validator, parsers):
    """
    Parses Union type
    Union type has to be parsed into multiple nodes
    in order to enable further validation of nested types
    """
    new_node = yield nodes.UnionNode()
    try:
        union_params = hint.__union_params__
    except AttributeError:
        union_params = hint.__args__
    validator.all_nodes.append(new_node)
    for element in union_params:
        yield get_parser(new_node, element, validator, parsers)
    yield _yield_parsing_result(node, new_node)


def _parse_type_var(node, hint, validator, parsers):
    try:
        new_node = validator.parent.roots[hint.__name__]
    except (KeyError, AttributeError):
        try:
            new_node = validator.globals[hint.__name__]
        except KeyError:
            covariant = hint.__covariant__
            contravariant = hint.__contravariant__
            new_node = yield nodes.TypeVarNode(covariant=covariant, contravariant=contravariant)
            if hint.__bound__ is not None:
                yield get_parser(new_node, hint.__bound__, validator, parsers)
            elif hint.__constraints__:
                for constraint in hint.__constraints__:
                    yield get_parser(new_node, constraint, validator, parsers)
            else:
                yield get_parser(new_node, typing.Any, validator, parsers)
            validator.globals[hint.__name__] = new_node
            validator.all_nodes.append(new_node)

    yield _yield_parsing_result(node, new_node)


def _parse_tuple(node, hint, validator, parsers):
    tuple_params = None
    try:
        if hint.__tuple_params__:
            tuple_params = list(hint.__tuple_params__)
            if hint.__tuple_use_ellipsis__:
                tuple_params.append(Ellipsis)
    except AttributeError:
        if hint.__args__:
            tuple_params = list(hint.__args__)

    if tuple_params is None:
        yield _parse_default(node, hint, validator, parsers)
    else:
        new_node = yield nodes.TupleNode(variable_length=(Ellipsis in tuple_params))
        for element in tuple_params:
            if element is not Ellipsis:
                yield get_parser(new_node, element, validator, parsers)
        yield _yield_parsing_result(node, new_node)


def _parse_callable(node, hint, validator, parsers):
    new_node = yield nodes.CallableNode(hint)
    validator.all_nodes.append(new_node)
    yield _yield_parsing_result(node, new_node)


def _parse_complex(node, hint, validator, parsers):
    """
    In Python both float and integer numbers can be used in place where
    complex numbers are expected
    """
    hints = [complex, int, float]
    yield _yield_unified_node(node, hints, validator, parsers)


def _parse_bytes(node, hint, validator, parsers):
    """
    Bytes should accept bytearray and memoryview, but not otherwise
    """
    hints = [bytearray, memoryview, bytes]
    yield _yield_unified_node(node, hints, validator, parsers)


def _parse_generic(node, hint, validator, parsers):
    if issubclass(hint, typing.List):
        yield _parse_list(node, hint, validator, parsers)
    elif issubclass(hint, typing.Mapping):
        yield _parse_dict(node, hint, validator, parsers)
    elif issubclass(hint, typing.Set):
        yield _parse_set(node, hint, validator, parsers)
    else:
        new_node = yield nodes.GenericNode(
            hint,
            covariant=validator.settings.covariant,
            contravariant=validator.settings.contravariant
        )
        validator.all_nodes.append(new_node)
        yield _yield_parsing_result(node, new_node)


def _parse_list(node, hint, validator, parsers):
    new_node = yield nodes.SimpleNode(hint.__extra__)
    validator.all_nodes.append(new_node)

    # add its type as child
    # We need to index first element only as Lists always have 1 argument
    if hint.__args__:
        yield get_parser(new_node, hint.__args__[0], validator, parsers)

    yield _yield_parsing_result(node, new_node)


def _parse_set(node, hint, validator, parsers):
    new_node = yield nodes.SimpleNode(hint.__extra__)
    validator.all_nodes.append(new_node)

    # add its type as child
    # We need to index first element only as Sets always have 1 argument
    if hint.__args__:
        yield get_parser(new_node, hint.__args__[0], validator, parsers)

    yield _yield_parsing_result(node, new_node)


def _parse_dict(node, hint, validator, parsers):
    hint_args = hint.__args__

    if hint_args:
        new_node = yield nodes.MappingNode(hint.__extra__)
        validator.all_nodes.append(new_node)

        yield get_parser(new_node, hint_args[0], validator, parsers)
        yield get_parser(new_node, hint_args[1], validator, parsers)

        yield _yield_parsing_result(node, new_node)

    else:
        yield _parse_default(node, hint, validator, parsers)


def _parse_forward_ref(node, hint, validator, parsers):
    new_node = yield nodes.ForwardRefNode(hint)
    validator.all_nodes.append(new_node)
    yield _yield_parsing_result(node, new_node)


def _parse_unwrapped_forward_ref(node, hint, validator, parsers):
    forward_ref = typing._ForwardRef(hint)
    yield _parse_forward_ref(node, forward_ref, validator, parsers)


def _yield_unified_node(node, hints, validator, parsers):
    new_node = yield nodes.UnionNode()
    validator.all_nodes.append(new_node)
    for element in hints:
        yield _parse_default(new_node, element, validator, parsers)
    yield _yield_parsing_result(node, new_node)


def _yield_parsing_result(node, new_node):
    # Potentially reducing the runtime efficiency
    # Need some evidences to decide what to do
    # with this piece of code next
    if node:
        node.add_child(new_node)
    else:
        yield new_node


def _fail_on_empty_protocol(node, hint, validator, parsers):
    raise TypeError('Cannot enforce undefined protocol')


TYPE_PARSERS = {
    UnionMeta: _parse_union,
    typing.TupleMeta: _parse_tuple,
    typing.GenericMeta: _parse_generic,
    typing.CallableMeta: _parse_callable,
    typing.TypeVar: _parse_type_var,
    typing._ForwardRef: _parse_forward_ref,
    EnhancedTypeVar: _parse_type_var,
    complex: _parse_complex,
    bytes: _parse_bytes
    }

TYPE_ERROR_GENERATORS = {
    _Protocol: _fail_on_empty_protocol
}


# For details, see the '_get_aliased_parser_or_default' docstring
ALIASED_TYPE_PARSERS = (
    ParserChoice(validator=is_named_tuple, parser=_parse_namedtuple),
    ParserChoice(validator=is_wrapped_generic, parser=_parse_generic)
    )
