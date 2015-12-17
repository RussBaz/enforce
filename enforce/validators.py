import typing

from .exceptions import RuntimeTypeError


handlers = {
    typing.Any: any_handler,
    typing.Union: union_handler,
    typing.Optional: union_handler
}

def any_handler(type_obj):
    return True

def union_handler(type_obj):
    sub_types = [x for x in type_obj.__union_params__]
    return many_children_handler(type_obj, sub_types, strict=True)

###################################################################

def defaul_handler(type_obj):
    validator = validators.get(type_obj, default_validator)
    return Node(validator)

def many_children_handler(type_obj, sub_types=None, strict=True):
    if sub_types is None:
        sub_types = []
    validator = validators.get(type_obj, default_validator)
    children = [build(x) for x in sub_types]
    return Node(validator, children, strict)

###################################################################

def build(type_obj):
    if type_obj is None:
        type_obj = type(None)

    handler = handlers.get(type_obj, defaul_handler)
    return handler(type_obj)

class Node:

    def __init__(self, validator, children=None, strict=True):
        if children is None:
            children = []

        self.validator = validator
        self.strict = strict
        self.children = children
    
    def validate(self, param, global_vars):
        pass


class Root:

    def __init__(self, node):
        self.global_vars = {
            type_vars: {},
            error_messages: []
        }
        self.node = node

    def validate(self):
        self.node.validate()

###################################################################

validators = {}

def default_validator():
    pass
