import unittest
from enforce.utils import visit
from enforce.nodes import CallableNode
from typing import Callable


class NodesTests(unittest.TestCase):
    pass


class CallableNodeTests(unittest.TestCase):
    def setUp(self):
        self.node = CallableNode(Callable[[int], int])
        self.any_node = CallableNode(Callable)
        self.any_input_node = CallableNode(Callable[..., int])

    def test_callable_validates_function(self):
        def add1(x: int) -> int:
            return x+1
        self.assertTrue(visit(self.node.validate(add1, '')).valid)

    def test_any_callable(self):
        def add(): pass

        self.assertTrue(visit(self.any_node.validate(add, '')).valid)

    def test_any_input_with_output(self):
        def sample_a(): pass
        def sample_b() -> int: pass
        def sample_C(a: int) -> int: pass
        def sample_d(a: int): pass

        self.assertFalse(visit(self.any_input_node.validate(sample_a, '')).valid)
        self.assertTrue(visit(self.any_input_node.validate(sample_b, '')).valid)
        self.assertTrue(visit(self.any_input_node.validate(sample_C, '')).valid)
        self.assertFalse(visit(self.any_input_node.validate(sample_d, '')).valid)

    def test_callable_validates_callable_object(self):
        class AddOne:
            def __call__(self, x: int) -> int:
                return x+1

        self.assertTrue(visit(self.node.validate(AddOne(), '')).valid)


if __name__ == '__main__':
    unittest.main()
