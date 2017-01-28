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

    def test_callable_validates_function(self):
        def add1(x: int) -> int:
            return x+1
        self.assertTrue(visit(self.node.validate(add1, '')).valid)

    def test_any_callable(self):
        def add(): pass

        self.assertTrue(visit(self.any_node.validate(add, '')).valid)

    def test_callable_validates_callable_object(self):
        class AddOne:
            def __call__(self, x: int) -> int:
                return x+1

        self.assertTrue(visit(self.node.validate(AddOne(), '')).valid)


if __name__ == '__main__':
    unittest.main()
