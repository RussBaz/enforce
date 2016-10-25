import unittest
from enforce.utils import visit
from enforce.nodes import CallableNode
from typing import Callable


class NodesTests(unittest.TestCase):
    pass


class CallableNodeTests(unittest.TestCase):
    def setUp(self):
        self.node = CallableNode(Callable[[int], int])

    def test_callable_validates_function(self):
        def add1(x: int) -> int:
            return x+1
        self.assertTrue(visit(self.node.validate(add1, '')))

    def test_callable_validates_callable_object(self):
        class AddOne:
            def __call__(self, x: int) -> int:
                return x+1

        self.assertTrue(visit(self.node.validate(AddOne(), '')))


if __name__ == '__main__':
    unittest.main()
