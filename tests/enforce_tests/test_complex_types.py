import numbers
import typing
import unittest

from enforce import runtime_validation, config
from enforce.exceptions import RuntimeTypeError
from enforce.types import EnhancedTypeVar


class ComplexTypesTests(unittest.TestCase):
    """
    Tests for the simple types which require special processing
    """

    def setUp(self):
        config(reset=True)

    def tearDown(self):
        config(reset=True)

    @staticmethod
    def get_type_var_func(configurable=False, type_var=None):
        if type_var is None:
            A = typing.TypeVar("A")
        else:
            A = type_var

        def type_var_func(data: A) -> A:
            return data

        def configurable_type_var_func(data: typing.Any, type_option: A) -> A:
            return data

        if configurable:
            return runtime_validation(configurable_type_var_func)
        else:
            return runtime_validation(type_var_func)

    def test_checking_mode(self):
        """
        Verifies that settings affect the selected type checking mode - covariant/contravariant
        """

        @runtime_validation
        def func(data: numbers.Integral):
            pass

        @runtime_validation
        def func2(data: typing.Union[float, str]):
            pass

        with self.assertRaises(RuntimeTypeError):
            func(1)

        with self.assertRaises(RuntimeTypeError):
            func(1.0)

        with self.assertRaises(RuntimeTypeError):
            func(True)

        func2("hello")
        func2(1.0)
        with self.assertRaises(RuntimeTypeError):
            func2(1)

        config({"mode": "covariant"})

        func(1)
        func(True)
        with self.assertRaises(RuntimeTypeError):
            func(1.0)

        func2("hello")
        func2(1.0)
        func2(1)

        config({"mode": "contravariant"})

        with self.assertRaises(RuntimeTypeError):
            func(1)

        func(1.0)

        with self.assertRaises(RuntimeTypeError):
            func(True)

        func2("hello")
        func2(1.0)
        with self.assertRaises(RuntimeTypeError):
            func2(1)

        config({"mode": "bivariant"})

        func(1)
        func(1.0)
        func(True)

        func2("hello")
        func2(1.0)
        func2(1)

        config({"mode": "invariant"})

        with self.assertRaises(RuntimeTypeError):
            func(1)

        with self.assertRaises(RuntimeTypeError):
            func(1.0)

        with self.assertRaises(RuntimeTypeError):
            func(True)

        func2("hello")
        func2(1.0)
        with self.assertRaises(RuntimeTypeError):
            func2(1)

    def test_optional(self):
        @runtime_validation
        def sample(data: typing.Optional[int]) -> typing.Optional[int]:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> typing.Union[int]:
            return data

        self.assertEqual(sample(1), 1)
        self.assertIsNone(sample(None))
        with self.assertRaises(RuntimeTypeError):
            sample("")

        with self.assertRaises(RuntimeTypeError):
            sample_bad("")

    def test_tuple(self):
        @runtime_validation
        def sample(data: typing.Tuple[int, str]) -> typing.Tuple[int, str]:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> typing.Tuple[int, str]:
            return data

        @runtime_validation
        def sample_any_in(data: typing.Tuple) -> typing.Tuple:
            return data

        @runtime_validation
        def sample_any_out(data: typing.Any) -> typing.Tuple:
            return data

        self.assertEqual(sample((1, "")), (1, ""))
        with self.assertRaises(RuntimeTypeError):
            sample((1, 1))

        with self.assertRaises(RuntimeTypeError):
            sample(())

        with self.assertRaises(RuntimeTypeError):
            sample([])

        with self.assertRaises(RuntimeTypeError):
            sample_bad((""))

        self.assertEqual(sample_any_in((1, "")), (1, ""))
        with self.assertRaises(RuntimeTypeError):
            sample_any_in(1)

        self.assertEqual(sample_any_out((1,)), (1,))
        with self.assertRaises(RuntimeTypeError):
            sample_any_out(1)

    def test_named_tuple(self):
        from collections import namedtuple

        MyNamedTuple = typing.NamedTuple("MyNamedTuple", [("my_int", int)])

        t = MyNamedTuple(5)
        t1 = namedtuple("MyNamedTuple", "my_int")(5)
        t2 = namedtuple("MyNamedTuple", "my_int")("string")
        t3 = runtime_validation(MyNamedTuple)(5)
        t4 = (5,)
        t5 = "5"

        @runtime_validation
        def sample(data: MyNamedTuple) -> MyNamedTuple:
            return data

        # invariant cases
        sample(t)
        with self.assertRaises(RuntimeTypeError):
            sample(t1)
        with self.assertRaises(RuntimeTypeError):
            sample(t2)
        sample(t3)
        with self.assertRaises(RuntimeTypeError):
            sample(t4)
        with self.assertRaises(RuntimeTypeError):
            sample(t5)

        # Covariant case
        config({"mode": "covariant"})

    def test_typed_named_tuple(self):
        MyNamedTuple = typing.NamedTuple("MyNamedTuple", [("my_int", int)])
        MyNamedTuple = runtime_validation(MyNamedTuple)

        mt = MyNamedTuple(5)
        mt2 = MyNamedTuple(my_int=5)

        self.assertEqual(mt[0], 5)
        self.assertEqual(mt.my_int, 5)

        self.assertEqual(mt2[0], 5)
        self.assertEqual(mt2.my_int, 5)

        with self.assertRaises(RuntimeTypeError):
            MyNamedTuple("string")

        with self.assertRaises(RuntimeTypeError):
            MyNamedTuple(my_int="string")

        with self.assertRaises(AttributeError):
            mt2.my_int = "hello world"

        with self.assertRaises(TypeError):
            MyNamedTuple(2, my_int="string")

    def test_variable_length_tuple(self):
        # TODO: What if tuple is empty?
        @runtime_validation
        def sample_in(data: typing.Tuple[int, ...]) -> typing.Any:
            return data

        @runtime_validation
        def sample_out(data: typing.Any) -> typing.Tuple[int, ...]:
            return data

        good = (1, 3, 4)
        bad = (1, "a", 2)
        empty = ()

        self.assertEqual(sample_in(good), good)
        self.assertEqual(sample_out(good), good)
        self.assertEqual(sample_in(empty), empty)
        self.assertEqual(sample_out(empty), empty)

        with self.assertRaises(RuntimeTypeError):
            sample_in(bad)

        with self.assertRaises(RuntimeTypeError):
            sample_out(bad)

    def test_simple_unbounded_type_var(self):
        type_var_func = self.get_type_var_func()
        bad_type_var_func = self.get_type_var_func(configurable=True)

        self.assertEqual(type_var_func(1), 1)
        self.assertEqual(bad_type_var_func("", "hello world"), "")

        with self.assertRaises(RuntimeTypeError):
            bad_type_var_func("", 1)

    def test_simple_bounded_type_var(self):
        # Invariant case
        A = typing.TypeVar("A", int, str)

        type_var_func = self.get_type_var_func(type_var=A)
        bad_type_var_func = self.get_type_var_func(configurable=True, type_var=A)

        self.assertEqual(type_var_func(1), 1)
        self.assertEqual(type_var_func(""), "")
        self.assertEqual(bad_type_var_func(1, 1), 1)
        self.assertEqual(bad_type_var_func("", ""), "")

        with self.assertRaises(RuntimeTypeError):
            type_var_func(1.0)

        with self.assertRaises(RuntimeTypeError):
            bad_type_var_func(1.0, 1)

    def test_covariant_type_var(self):
        A = typing.TypeVar("A", bound=numbers.Number, covariant=True)

        type_var_func = self.get_type_var_func(type_var=A)

        self.assertEqual(type_var_func(1), 1)
        self.assertEqual(type_var_func(1.0), 1.0)
        self.assertEqual(type_var_func(1 + 1j), 1 + 1j)

        with self.assertRaises(RuntimeTypeError):
            type_var_func("bad")

    def test_contravariant_type_var(self):
        class B(object):
            pass

        class C(B):
            pass

        class D(C):
            pass

        A = typing.TypeVar("A", bound=C, contravariant=True)

        b = B()
        c = C()
        d = D()

        type_var_func = self.get_type_var_func(type_var=A)

        self.assertIs(type_var_func(c), c)
        self.assertIs(type_var_func(b), b)

        with self.assertRaises(RuntimeTypeError):
            type_var_func(d)

    def test_bivariant_type_var(self):
        class B(object):
            pass

        class C(B):
            pass

        class D(C):
            pass

        A = EnhancedTypeVar("A", bound=C, covariant=True, contravariant=True)

        b = B()
        c = C()
        d = D()

        type_var_func = self.get_type_var_func(type_var=A)

        self.assertIs(type_var_func(c), c)
        self.assertIs(type_var_func(b), b)
        self.assertIs(type_var_func(d), d)

        with self.assertRaises(RuntimeTypeError):
            type_var_func("bad")


if __name__ == "__name__":
    unittest.main()
