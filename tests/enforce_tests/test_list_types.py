import typing
import unittest

from enforce import runtime_validation
from enforce.exceptions import RuntimeTypeError


class ListTypesTests(unittest.TestCase):
    def setUp(self):
        @runtime_validation
        def str_func(x: typing.List[str]) -> str:
            return x[0]

        self.str_func = str_func

        @runtime_validation
        def int_func(x: typing.List[int]) -> int:
            return x[0]

        self.int_func = int_func

        def int_str_func(x: typing.List[typing.Union[str, int]]) -> int:
            return int(x[0])

        self.union_func = int_str_func

    def test_str_list(self):
        self.str_func(["a"])
        self.str_func(["a", "b", "c"])

        with self.assertRaises(RuntimeTypeError):
            self.str_func(3)

        with self.assertRaises(RuntimeTypeError):
            self.str_func("3")

        with self.assertRaises(RuntimeTypeError):
            self.str_func([1, 2, 3])

        with self.assertRaises(RuntimeTypeError):
            self.str_func([1, "b", 5.0])

        with self.assertRaises(RuntimeTypeError):
            self.str_func(["a", 1, "b", 5.0])

    def test_int_list(self):
        self.int_func([1])
        self.int_func([1, 2, 3])

        with self.assertRaises(RuntimeTypeError):
            self.int_func(5)

        with self.assertRaises(RuntimeTypeError):
            self.int_func("5")

        with self.assertRaises(RuntimeTypeError):
            self.int_func(["1", "2", "a"])

        with self.assertRaises(RuntimeTypeError):
            self.int_func(["a", 1, "b", 5.0])

    def test_union_func(self):
        self.union_func([1])
        self.union_func([1, 2, 3])
        self.union_func(["1"])
        self.union_func(["1", "2", "3"])
        self.union_func([1, "2", 3, "4"])
        self.union_func(["1", 2, "3", 4])

        with self.assertRaises(RuntimeTypeError):
            self.int_func(1)

        with self.assertRaises(RuntimeTypeError):
            self.int_func("a")

        with self.assertRaises(RuntimeTypeError):
            self.int_func([[1, 2, 3], "4"])

        with self.assertRaises(RuntimeTypeError):
            self.int_func(["a", "b", {3, 4, 5}])

    def test_list_of_lists(self):
        @runtime_validation
        def func(param: typing.List[typing.List[str]]) -> typing.List[typing.List[str]]:
            return param

        func([["s", "aaa"], ["a", "b"]])
        func([[]])

        with self.assertRaises(RuntimeTypeError):
            func([[12]])


if __name__ == "__name__":
    unittest.main()
