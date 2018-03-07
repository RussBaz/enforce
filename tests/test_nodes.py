import pytest

from enforce.utils import run_lazy_function
from enforce.nodes import CallableNode
from enforce.validator import Validator
from enforce.settings import Settings
from typing import Callable


class TestNodes:
    pass


class TestCallableNodes:
    def setup_method(self):
        self.node = CallableNode(Callable[[int], int])
        self.any_node = CallableNode(Callable)
        self.any_input_node = CallableNode(Callable[..., int])
        self.validator = Validator(Settings(enabled=True, group='default'))

    def test_callable_validates_function(self):
        def add1(x: int) -> int:
            return x+1

        def add2(x: str) -> str:
            return x

        assert run_lazy_function(self.validator.validate_lazy(self.node, add1)).valid
        assert not run_lazy_function(self.validator.validate_lazy(self.node, add2)).valid

    def test_any_callable(self):
        def add(): pass

        assert run_lazy_function(self.validator.validate_lazy(self.any_node, add)).valid

    def test_any_input_with_output(self):
        def sample_a(): pass
        def sample_b() -> int: pass
        def sample_c(a: int) -> int: pass
        def sample_d(a: int): pass

        assert not run_lazy_function(self.validator.validate_lazy(self.any_input_node, sample_a)).valid
        assert run_lazy_function(self.validator.validate_lazy(self.any_input_node, sample_b)).valid
        assert run_lazy_function(self.validator.validate_lazy(self.any_input_node, sample_c)).valid
        assert not run_lazy_function(self.validator.validate_lazy(self.any_input_node, sample_d)).valid

    def test_callable_validates_callable_object(self):
        class AddOne:
            def __call__(self, x: int) -> int:
                return x+1

        assert AddOne()(1) == 2
        assert run_lazy_function(self.validator.validate_lazy(self.node, AddOne())).valid
