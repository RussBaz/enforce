import typing
import unittest

from enforce import runtime_validation
from enforce.exceptions import RuntimeTypeError


class TestContainerTypes(unittest.TestCase):
    """
    Tests for the container types - including types of unbounded size
    """

    def test_forward_reference_container(self):
        @runtime_validation
        def foo(data: typing.Optional["A"]):
            return data.bar(10)

        @runtime_validation
        def bar(data: "B"):
            return data

        class A(object):
            def __init__(self, value: int):
                self.value = value

            def bar(self, value: int):
                return self.value * 2 + value

        class B(object):
            pass

        a = A(12)

        self.assertEqual(foo(a), 34)
        self.assertIsInstance(bar(B()), B)

        with self.assertRaises(RuntimeTypeError):
            foo(12)

        with self.assertRaises(RuntimeTypeError):
            bar("B")


if __name__ == "__name__":
    unittest.main()
