import typing
import unittest

from enforce import runtime_validation
from enforce.exceptions import RuntimeTypeError


class CallableTypesTests(unittest.TestCase):
    """
    Tests for the callable types such as functions
    """

    def setUp(self):
        @runtime_validation
        def test(func: typing.Callable[[int, int], int], x: int) -> int:
            return func(x, x)

        @runtime_validation
        def test_list(
            func: typing.Callable[[typing.Union[typing.List[typing.Any], int]], int]
        ) -> int:
            return func(5)

        @runtime_validation
        def union(
            func: typing.Callable[[typing.Union[float, int], typing.Optional[str]], int]
        ) -> int:
            return func(5)

        @runtime_validation
        def any_func_args(func: typing.Callable):
            return func

        @runtime_validation
        def any_func_return(func) -> typing.Callable:
            return func

        self.test = test
        self.test_list = test_list
        self.union = union
        self.any_func_args = any_func_args
        self.any_func_return = any_func_return

    # TODO: rename this test
    def test_unrestrained_callable_arguments(self):
        """
        Verifies that a function which expects any Callable as an argument,
        would fail if an object of different type is passed
        """
        callable = lambda x: x
        self.any_func_args(callable)

        with self.assertRaises(RuntimeTypeError):
            self.any_func_args("bad_input")

    # TODO: rename this test
    def test_unrestrained_callable_returns(self):
        """
        Verifies that a function which expects any Callable as an output,
        would fail if an object of different type is returned
        """
        callable = lambda x: x
        self.any_func_return(callable), callable

        with self.assertRaises(RuntimeTypeError):
            self.any_func_return("bad_input")

    def test_good_callable_object(self):
        """Test that a callable object works"""

        class Good(object):
            def __call__(self, x: int, y: int) -> int:
                return int(x * y)

        self.test(Good(), 5)

    def test_good_func_arg(self):
        """Test that good arguments pass"""

        def good(x: int, y: int) -> int:
            return int(x * y)

        self.test(good, 5)

    def test_bad_func_return(self):
        """
        Test that a function being passed in with mismatching return raises
        """

        def bad_return(x: int, y: int) -> float:
            return float(x * y)

        with self.assertRaises(RuntimeTypeError):
            self.test(bad_return, 5)

    def test_bad_func_call(self):
        """
        Test that a function being passed in with mismatching callsig raises
        """

        def bad_callsig(x: str, y: str) -> int:
            return int(x + y)

        with self.assertRaises(RuntimeTypeError):
            self.test(bad_callsig, 5)

    def test_bad_func(self):
        """
        Test that passing in something that's not a function raises
        """
        with self.assertRaises(RuntimeTypeError):
            self.test(5, 5)

    def test_nested_func(self):
        """
        Test that a function with deeply nested types works
        """

        def nest_func(x: typing.Union[int, typing.List[typing.Any]]) -> int:
            return 5

        self.test_list(nest_func)

    def test_nested_bad_func(self):
        """
        Test that a function with bad deeply nested types fails
        """

        def nest_func(x: typing.List[typing.List[int]]) -> int:
            return 5

        with self.assertRaises(RuntimeTypeError):
            self.test_list(nest_func)

    def test_good_union_func(self):
        def good_union(
            x: typing.Union[float, int], a: typing.Optional[str] = None
        ) -> int:
            print(a)
            return int(x)

        self.union(good_union)

    def test_bad_union_func(self):
        def bad_union(x: float, a=None) -> int:
            return int(x)

        with self.assertRaises(RuntimeTypeError):
            self.union(bad_union)

    def test_good_optional_parameter_func(self):
        def good_param(
            x: typing.Union[float, int], y: typing.Optional[str] = "a"
        ) -> int:
            return x

        self.union(good_param)

    def test_bad_optional_parameter_func(self):
        def bad_param(x: typing.Union[float, int], y: str = "b") -> int:
            return x

        with self.assertRaises(RuntimeTypeError):
            self.union(bad_param)


if __name__ == "__name__":
    unittest.main()
