import typing

from .nodes import BaseNode
from .parsers import get_parser
from .utils import visit


class Validator:

    def __init__(self, parent: typing.Optional['Validator']=None):
        self.parent = parent
        self.settings = None
        self.errors = []
        self.globals = {}
        self.data_out = {}
        self.roots = {}
        self.all_nodes = []

    def validate(self, data: typing.Any, param_name: str) -> bool:
        """
        Validate Syntax Tree of given function using generators
        """
        hint_validator = self.roots[param_name]
        validation_tree = hint_validator.validate(data, self)

        validation_result = visit(validation_tree)

        self.data_out[param_name] = self.roots[param_name].data_out

        if not validation_result.valid:
            self.errors.append((param_name, validation_result.type_name))

        return validation_result.valid

    def reset(self) -> None:
        """
        Prepares the validator for yet another round of validation by clearing all the temporary data
        """
        self.errors = []
        self.data_out = {}
        for node in self.all_nodes:
            node.reset()
        if self.parent is not None:
            self.parent.reset()

    #def __str__(self) -> str:
    #    """
    #    Returns a debugging info abuot the validator's current status
    #    """
    #    local_nodes = [str(tree) for hint, tree in self.roots.items() if hint != 'return']
    #    str_repr = '[{}]'.format(', '.join(local_nodes))
    #    try:
    #        # If doesn't necessarily have return value, we need to not return one.
    #        str_repr += ' => {}'.format(self.roots['return'])
    #    except KeyError:
    #        pass
    #    return str_repr


def init_validator(hints: typing.Dict, parent: typing.Optional[Validator]=None) -> Validator:
    """
    Returns a new validator instance from a given dictionary of type hints
    """
    validator = Validator(parent)

    for name, hint in hints.items():
        if hint is None:
            hint = type(None)

        root_parser = get_parser(None, hint, validator)
        syntax_tree = visit(root_parser)

        validator.roots[name] = syntax_tree

    return validator
