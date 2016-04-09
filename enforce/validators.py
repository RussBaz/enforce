from .utils import visit


class Validator:

    def __init__(self):
        self.errors = []
        self.globals = {}
        self.data_out = {}
        self.roots = {}
        self.all_nodes = []

    def validate(self, data, param_name):
        """
        Validate Syntax Tree using generators
        """
        validators = self._validate(self.roots[param_name], data)
        result = visit(validators)
        self.data_out[param_name] = self.roots[param_name].data_out
        if not result:
            self.errors.append(param_name)
        return result

    def reset(self):
        self.errors = []
        self.data_out = {}
        for node in self.all_nodes:
            node.reset()

    def _validate(self, node, data):
        yield node.validate(data, self)
