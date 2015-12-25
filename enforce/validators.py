import typing
from abc import ABC, abstractclassmethod

from .exceptions import RuntimeTypeError


class BaseNode(ABC):

    def __init__(self, data_type, strict, type_var=False):
        self.data_type = data_type
        self.strict = strict
        self.type_var = type_var

        self.data_out = None
        self.last_type = None
        self.original_children = []
        self.children = []

    def validate(self, data, validator, force=False):
        valid = self.validate_data(validator, data, force)

        if not valid:
            yield False
            raise StopIteration
        
        results = []
        propogated_data = self.map_data(validator, data)

        # Not using zip because it will silence a mismatch in sizes
        # between children and propogated_data
        # And, for now, at least, I'd prefer it be explicit
        for i, child in enumerate(self.children):
            result = yield child.validate(propogated_data[i], validator, self.type_var)
            results.append(result)

        if self.strict:
            valid = all(results)
        else:
            valid = any(results)

        if not valid:
            yield False
            raise StopIteration

        returned_data = [a.data_out for a in self.children]
        self.data_out = self.reduce_data(validator, returned_data, data)

        if results and force:
            self.children = [self.children[results.index(True)]]

        self.last_type = type(data)
        yield True

    @abstractclassmethod
    def validate_data(self, validator, data, sticky=False):
        pass

    @abstractclassmethod
    def map_data(self, validator, data):
        pass

    @abstractclassmethod
    def reduce_data(self, validator, data, old_data):
        pass

    def add_child(self, child):
        self.children.append(child)
        self.original_children.append(child)

    def reset(self):
        self.data_out = None
        self.last_type = None
        self.children = [a for a in self.original_children]


class SimpleNode(BaseNode):
    
    def __init__(self, data_type):
        return super().__init__(data_type, True, True)

    def validate_data(self, validator, data, sticky=False):
        # Will keep till all the debugging is over
        #print('Validation:', data, self.data_type)
        return issubclass(type(data), self.data_type)

    def map_data(self, validator, data):
        return []

    def reduce_data(self, validator, data, old_data):
        return old_data


class UnionNode(BaseNode):

    def __init__(self):
        return super().__init__(typing.Any, False)

    def validate_data(self, validator, data, sticky=False):
        # Will keep till all the debugging is over
        #print('Validation:', data, self.data_type)
        if sticky and self.last_type is not None:
            return type(data) == self.last_type
        return True

    def map_data(self, validator, data):
        output = []
        for _ in self.children:
            output.append(data)
        return output

    def reduce_data(self, validator, data, old_data):
        for element in data:
            if element is not None:
                return element
        else:
            return None


class TypeVarNode(BaseNode):

    def __init__(self):
        return super().__init__(typing.Any, False, True)

    def validate_data(self, validator, data, sticky=False):
        return True

    def map_data(self, validator, data):
        return [data]

    def reduce_data(self, validator, data, old_data):
        return data[0]


class Validator:

    def __init__(self):
        self.errors = []
        self.globals = {}
        self.data_out = {}
        self.roots = {}
        self.all_nodes = []
    
    def validate(self, data, param_name):
        validatiors = self._validate(self.roots[param_name], data, self)
        result = visit(validatiors)
        self.data_out[param_name] = self.roots[param_name].data_out
        if not result:
            self.errors.append(param_name)
        return result

    def reset(self):
        self.errors = []
        self.data_out = {}
        for node in self.all_nodes:
            node.reset()

    @staticmethod
    def _validate(node, data, visitor):
        yield node.validate(data, visitor)


def visit(generator):
    stack = [generator]
    last_result = None
    while stack:
        try:
            last = stack[-1]
            if isinstance(last, typing.Generator):
                stack.append(last.send(last_result))
                last_result = None
            else:
                last_result = stack.pop()
        except StopIteration:
            stack.pop()
    return last_result
