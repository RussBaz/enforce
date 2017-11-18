import unittest
from enforce.utils import visit
from enforce.nodes import CallableNode
from enforce.settings import Settings
from typing import Callable


class NodesTests(unittest.TestCase):
    pass


class CallableNodeTests(unittest.TestCase):
    def setUp(self):
        class SampleValidator:
            def __init__(self, settings):
                self.settings = settings

        self.node = CallableNode(Callable[[int], int])
        self.any_node = CallableNode(Callable)
        self.any_input_node = CallableNode(Callable[..., int])
        self.validator = SampleValidator(Settings(enabled=True, group='default'))

    def test_callable_validates_function(self):
        def add1(x: int) -> int:
            return x+1

        def add2(x: str) -> str:
            return x

        self.assertTrue(visit(self.node.validate(add1, self.validator)).valid)
        self.assertFalse(visit(self.node.validate(add2, self.validator)).valid)

    def test_any_callable(self):
        def add(): pass

        self.assertTrue(visit(self.any_node.validate(add, self.validator)).valid)

    def test_any_input_with_output(self):
        def sample_a(): pass
        def sample_b() -> int: pass
        def sample_C(a: int) -> int: pass
        def sample_d(a: int): pass

        self.assertFalse(visit(self.any_input_node.validate(sample_a, self.validator)).valid)
        self.assertTrue(visit(self.any_input_node.validate(sample_b, self.validator)).valid)
        self.assertTrue(visit(self.any_input_node.validate(sample_C, self.validator)).valid)
        self.assertFalse(visit(self.any_input_node.validate(sample_d, self.validator)).valid)

    def test_callable_validates_callable_object(self):
        class AddOne:
            def __call__(self, x: int) -> int:
                return x+1

        self.assertTrue(AddOne()(1), 2)
        self.assertTrue(visit(self.node.validate(AddOne(), self.validator)).valid)


if __name__ == '__main__':
    unittest.main()
