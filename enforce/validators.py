import typing

from .utils import visit
from .nodes import BaseNode


class Validator:

    def __init__(self):
        self.errors = []
        self.globals = {}
        self.data_out = {}
        self.roots = {}
        self.all_nodes = []

    def validate(self, data: typing.Any, param_name: str) -> bool:
        """
        Validate Syntax Tree of given function using generators
        """
        validators = self._validate(self.roots[param_name], data)
        result = visit(validators)
        self.data_out[param_name] = self.roots[param_name].data_out
        if not result:
            self.errors.append((param_name, type(data)))
        return result

    def reset(self) -> None:
        self.errors = []
        self.data_out = {}
        for node in self.all_nodes:
            node.reset()

    def _validate(self, node: BaseNode, data: typing.Any) -> typing.Generator:
        yield node.validate(data, self)
