import typing

from . import domain_types as dt
from .nodes import BaseNode
from .parsers import get_parser
from .settings import Settings
from .utils import run_lazy_function


class Validator:
    def __init__(self, settings: Settings, parent: typing.Optional["Validator"] = None):
        self.parent = parent
        self.settings = settings
        self.errors = []
        self.globals = {}
        self.locals = {}
        self.data_out = {}
        self.roots = {}
        self.all_nodes = []

    def validate(self, data: typing.Any, param_name: str) -> bool:
        """
        Validate Syntax Tree of given function using generators
        """
        hint_validator = self.roots[param_name]
        validation_tree = self.validate_lazy(hint_validator, data, self)

        validation_result = run_lazy_function(validation_tree)

        self.data_out[param_name] = self.roots[param_name].data_out

        if not validation_result.valid:
            self.errors.append((param_name, validation_result.type_name))

        return validation_result.valid

    def reset(self) -> None:
        """
        Prepares the validator for yet another round of validation by clearing all the temporary data
        """
        self.errors = []
        self.locals = {}
        self.globals = {}
        self.data_out = {}
        for node in self.all_nodes:
            node.reset()
        if self.parent is not None:
            self.parent.reset()

    # def __str__(self) -> str:
    #    """
    #    Returns a debugging info about the validator's current status
    #    """
    #    local_nodes = [str(tree) for hint, tree in self.roots.items() if hint != 'return']
    #    str_repr = '[{}]'.format(', '.join(local_nodes))
    #    try:
    #        # If doesn't necessarily have return value, we need to not return one.
    #        str_repr += ' => {}'.format(self.roots['return'])
    #    except KeyError:
    #        pass
    #    return str_repr

    def validate_lazy(
        self: "Validator", node: BaseNode, data: typing.Any, force: bool = False
    ) -> dt.ValidationResult:
        """
        Triggers all the stages of data validation, returning true or false as a result
        """
        # Preprocessing step for a forward reference evaluation

        if hasattr(node, "forward_ref") and not node.forward_ref.__forward_evaluated__:
            global_vars = self.globals
            local_vars = self.locals
            evaluated_type = typing._eval_type(
                node.forward_ref, global_vars, local_vars
            )
            parser = get_parser(node, evaluated_type, self)
            run_lazy_function(parser)

        # Validation steps:
        # 1. Pre-process (clean) incoming data
        # 2. Validate data
        # 3. If validated, map (distribute) data to child nodes. Otherwise - FAIL.
        # 4. Validate data at each node
        # 5. If sequence, all nodes must successfully validate date. Otherwise, at least one.
        # 6. If validated, reduce (collect) data from child nodes. Otherwise - FAIL.
        # 7. Post-process (clean) the resultant data
        # 8. Sets the output data for the node
        # 9. Indicate validation SUCCESS

        # 1
        clean_data = node.preprocess_data(self, data)

        # 2
        self_validation_result = node.validate_data(self, clean_data, force)

        # 3
        if not self_validation_result.valid and not node.is_container:
            yield self_validation_result
            return

        propagated_data = node.map_data(self, self_validation_result)

        # 4
        child_validation_results = yield node.validate_children(self, propagated_data)

        # 5
        if node.is_sequence:
            valid = all(result.valid for result in child_validation_results)
        else:
            valid = any(result.valid for result in child_validation_results)

        actual_type = node.get_actual_data_type(
            self_validation_result, child_validation_results, valid
        )

        # 6
        if not valid or not self_validation_result.valid:
            yield dt.ValidationResult(False, self_validation_result.data, actual_type)
            return

        reduced_data = node.reduce_data(
            self, self_validation_result, child_validation_results
        )

        # 7
        data_out = node.postprocess_data(self, reduced_data)

        # 8
        node.set_out_data(self, data, data_out)

        # 8/9
        yield dt.ValidationResult(True, data_out, actual_type)


def init_validator(
    settings, hints: typing.Dict, parent: typing.Optional[Validator] = None
) -> Validator:
    """
    Returns a new validator instance from a given dictionary of type hints
    """
    validator = Validator(settings, parent)

    for name, hint in hints.items():
        if hint is None:
            hint = type(None)

        root_parser = get_parser(None, hint, validator)
        syntax_tree = run_lazy_function(root_parser)

        validator.roots[name] = syntax_tree

    return validator
