import unittest
from typing import Callable

from enforce.nodes import CallableNode
from enforce.settings import Settings
from enforce.utils import run_lazy_function
from enforce.validator import Validator


class TestNodes(object):
    pass


class TestCallableNodes(unittest.TestCase):
    def setup_method(self):
        self.node = CallableNode(Callable[[int], int])
        self.any_node = CallableNode(Callable)
        self.any_input_node = CallableNode(Callable[..., int])
        self.validator = Validator(Settings(enabled=True, group="default"))

    def test_callable_validates_function(self):
        def add1(x: int) -> int:
            return x + 1

        def add2(x: str) -> str:
            return x

        self.assertTrue(
            run_lazy_function(self.validator.validate_lazy(self.node, add1)).valid
        )
        self.assertFalse(
            run_lazy_function(self.validator.validate_lazy(self.node, add2)).valid
        )

    def test_any_callable(self):
        def add():
            pass

        self.assertTrue(
            run_lazy_function(self.validator.validate_lazy(self.any_node, add)).valid
        )

    def test_any_input_with_output(self):
        def sample_a():
            pass

        def sample_b() -> int:
            pass

        def sample_c(a: int) -> int:
            pass

        def sample_d(a: int):
            pass

        self.assertFalse(
            run_lazy_function(
                self.validator.validate_lazy(self.any_input_node, sample_a)
            ).valid
        )
        self.assertTrue(
            run_lazy_function(
                self.validator.validate_lazy(self.any_input_node, sample_b)
            ).valid
        )
        self.assertTrue(
            run_lazy_function(
                self.validator.validate_lazy(self.any_input_node, sample_c)
            ).valid
        )
        self.assertFalse(
            run_lazy_function(
                self.validator.validate_lazy(self.any_input_node, sample_d)
            ).valid
        )

    def test_callable_validates_callable_object(self):
        class AddOne(object):
            def __call__(self, x: int) -> int:
                return x + 1

        self.assertEqual(AddOne()(1), 2)
        self.assertTrue(
            run_lazy_function(self.validator.validate_lazy(self.node, AddOne())).valid
        )


if __name__ == "__main__":
    unittest.main()
