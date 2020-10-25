import typing
import unittest

from enforce import runtime_validation
from enforce.exceptions import RuntimeTypeError


class UnionTypesTests(unittest.TestCase):
    """
    Test case for Union Types
    """

    def setUp(self):
        @runtime_validation
        def test_func(x: typing.Union[float, typing.List[str]]) -> int:
            return 5

        @runtime_validation
        def nest_func(
            x: typing.Union[float, typing.List[typing.Union[str, int]]]
        ) -> int:
            return 5

        self.test_func = test_func
        self.nest_func = nest_func

    def test_basic_union(self):
        @runtime_validation
        def sample(data: typing.Union[int, str]) -> typing.Union[int, str]:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> typing.Union[int, str]:
            return data

        self.assertEqual(sample(1), 1)
        self.assertEqual(sample(""), "")
        with self.assertRaises(RuntimeTypeError):
            sample(b"")

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1.0)

    def test_good_nested_union(self):
        self.test_func(5.0)
        self.test_func(["1", "2", "a"])

    def test_bad_nested_union(self):
        with self.assertRaises(RuntimeTypeError):
            self.test_func("a")

        with self.assertRaises(RuntimeTypeError):
            self.test_func([1, 2, 3, 4])

        with self.assertRaises(RuntimeTypeError):
            self.test_func(["a", 4, 5])

    def test_nested_func_good(self):
        self.nest_func(5.0)
        self.nest_func(["a", "b", "c"])
        self.nest_func([1, 2, 3])
        self.nest_func([1, "a", 2, "b"])

    def test_nested_func_bad(self):
        with self.assertRaises(RuntimeTypeError):
            self.nest_func("a")
        with self.assertRaises(RuntimeTypeError):
            self.nest_func({"a": 5, "b": 6})
        with self.assertRaises(RuntimeTypeError):
            self.nest_func({1, 2, 3, 4})

    def test_union_of_nested_lists(self):
        ManyMessageType = typing.List[str]
        MessagesType = typing.Union[str, typing.List[ManyMessageType]]

        @runtime_validation
        def test(msgs: MessagesType):
            return msgs

        test([["a", "b"], ["x", "y"]])
