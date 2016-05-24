import typing

from enforce import nodes
from .validators import Validator
from .utils import visit


class Parser:

    def __init__(self):
        self.validator = Validator()
        self._mapping = {
            typing.UnionMeta: self._parse_union,
            typing.TypeVar: self._parse_type_var,
            typing.TupleMeta: self._parse_tuple,
            typing.GenericMeta: self._parse_generic,
            typing.CallableMeta: self._parse_callable,
            complex: self._parse_complex,
            float: self._parse_float,
            bytes: self._parse_bytes
            }

    def __str__(self) -> str:
        local_nodes = [str(tree) for hint, tree in self.validator.roots.items() if hint != 'return']
        str_repr = '[{}]'.format(', '.join(local_nodes))
        try:
            # If doesn't necessarily have return value, we need to not return one.
            str_repr += ' => {}'.format(self.validator.roots['return'])
        except KeyError:
            pass
        return str_repr

    def parse(self, hint_type: type, hint_name: str) -> None:
        parsers = self._map_parser(None, hint_type, self)
        tree = visit(parsers)
        self.validator.roots[hint_name] = tree

    def _map_parser(self, node, hint: type, caller):
        if type(hint) == type:
            parser = self._mapping.get(hint, self._parse_default)
        else:
            parser = self._mapping.get(type(hint), self._parse_default)
        yield parser(node, hint, caller)

    def _parse_default(self, node, hint, parser):
        new_node = yield nodes.SimpleNode(hint)
        parser.validator.all_nodes.append(new_node)
        yield self._yield_parsing_result(node, new_node)

    def _parse_union(self, node, hint, parser):
        """
        Parses Union type
        Union type has to be parsed into multiple nodes
        in order to enable further validation of nested types
        """
        new_node = yield nodes.UnionNode()
        parser.validator.all_nodes.append(new_node)
        for element in hint.__union_params__:
            yield self._map_parser(new_node, element, parser)
        yield self._yield_parsing_result(node, new_node)

    def _parse_type_var(self, node, hint, parser):
        try:
            global_node = parser.validator.globals[hint.__name__]
        except KeyError:
            global_node = yield nodes.UnionNode()
            if hint.__constraints__:
                for constraint in hint.__constraints__:
                    yield self._map_parser(global_node, constraint, parser)
            else:
                yield self._map_parser(global_node, typing.Any, parser)
            parser.validator.globals[hint.__name__] = global_node
            parser.validator.all_nodes.append(global_node)

        new_node = yield nodes.TypeVarNode()
        new_node.add_child(global_node)
        parser.validator.all_nodes.append(new_node)
        yield self._yield_parsing_result(node, new_node)

    def _parse_callable(self, node, hint, parser):
        new_node = yield nodes.CallableNode()
        # Add every argument as a child
        for element in hint.__args__:
            yield self._map_parser(new_node, element, parser)
        # Add return type as child
        yield self._map_parser(new_node, hint.__result__, parser)
        yield self._yield_parsing_result(node, new_node)

    def _parse_tuple(self, node, hint, parser):
        if hint.__tuple_params__ is None:
            yield self._parse_default(node, hint, parser)
        else:
            new_node = yield nodes.TupleNode()
            for element in hint.__tuple_params__:
                yield self._map_parser(new_node, element, parser)
            yield self._yield_parsing_result(node, new_node)

    def _parse_callable(self, node, hint, parser):
        new_node = yield nodes.CallableNode(hint)
        parser.validator.all_nodes.append(new_node)
        yield self._yield_parsing_result(node, new_node)

    def _parse_complex(self, node, hint, parser):
        """
        In Python both float and integer numbers can be used in place where
        complex numbers are expected
        """
        hints = [complex, int, float]
        yield self._yield_unified_node(node, hints, parser)

    def _parse_float(self, node, hint, parser):
        """
        Floats should accept integers as well, but not otherwise
        """
        hints = [int, float]
        yield self._yield_unified_node(node, hints, parser)

    def _parse_bytes(self, node, hint, parser):
        """
        Floats should accept integers as well, but not otherwise
        """
        hints = [bytearray, memoryview, bytes]
        yield self._yield_unified_node(node, hints, parser)

    def _parse_generic(self, node, hint, parser):
        if issubclass(hint, typing.List):
            yield self._parse_list(node, hint, parser)
        else:
            yield self._parse_default(node, hint, parser)

    def _parse_list(self, node, hint, parser):
        new_node = yield nodes.SimpleNode(hint)
        parser.validator.all_nodes.append(new_node)

        # add its type as child
        # We can index first as Lists only ever have 1 parameter
        yield self._map_parser(new_node, hint.__parameters__[0], parser)

        yield self._yield_parsing_result(node, new_node)

    def _yield_unified_node(self, node, hints, parser):
        new_node = yield nodes.UnionNode()
        parser.validator.all_nodes.append(new_node)
        for element in hints:
            yield self._parse_default(new_node, element, parser)
        yield self._yield_parsing_result(node, new_node)

    def _yield_parsing_result(self, node, new_node):
        # Potentially reducing the runtime efficiency
        # Need some evidences to decide what to do
        # with this piece of code next
        if node:
            node.add_child(new_node)
        else:
            yield new_node


def init_validator(hints: typing.Dict) -> Parser:
    """
    Returns a new validator instance from a given dictionary of type hints
    """
    parser = Parser()
    for name, hint in hints.items():
        if hint is None:
            hint = type(None)
        parser.parse(hint, name)

    return parser.validator
