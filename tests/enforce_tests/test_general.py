import unittest
import typing

from enforce import runtime_validation, config
from enforce.exceptions import RuntimeTypeError


class GeneralTests(unittest.TestCase):
    """
    A container for general tests
    """

    def setUp(self):
        config(reset=True)

    def tearDown(self):
        config(reset=True)

    def test_argument_validation(self):
        self.assertEqual(self.sample_function('11', 1), 12)

        result = 0
        with self.assertRaises(RuntimeTypeError):
            result += self.sample_function(1, 2)

        self.assertEqual(result, 0)

    def test_returns_output_if_no_return_annotation(self):
        """
        Verifies that the wrapped function's output is returned even if there
        is no 'return' annotation
        """
        @runtime_validation
        def example(x: int):
            return x

        self.assertEqual(example(1), 1)

    def test_return_value_validation(self):
        self.assertIsNone(self.sample_function('', None))

        result = 0
        with self.assertRaises(RuntimeTypeError):
            result += self.sample_function('', 1)

        self.assertEqual(result, 0)

    def test_no_type_check(self):
        """
        Verifies that no_type_check is respected
        """
        def get_sample_func():
            def sample(data: int):
                pass

            return sample

        sample_d1 = typing.no_type_check(runtime_validation(get_sample_func()))
        sample_d2 = runtime_validation(typing.no_type_check(get_sample_func()))

        sample_d3 = runtime_validation(get_sample_func())

        get_sample_func()('str')
        sample_d1('str')
        sample_d2('str')
        with self.assertRaises(RuntimeTypeError):
            sample_d3('str')

    def test_any_code_works_with_modes(self):
        config({'mode': 'covariant'})

        @runtime_validation
        def example() -> typing.Optional[str]:
            return None

        example()

        class A:
            pass

        class B(A):
            pass

        a = A()
        b = B()

        @runtime_validation
        def foo(data: A):
            return data

        foo(a)
        foo(b)

        config(reset=True)

        foo(a)

        with self.assertRaises(RuntimeTypeError):
            foo(b)

    def test_instance_methods_as_arguments(self):
        """
        Verifies that the methods of an instance can be used as arguments for decorated function calls
        """
        class Sample:
            @runtime_validation
            def method(self, a: typing.Dict):
                return a

            @runtime_validation
            def method_bad(self, a: typing.List):
                return [a]

        s = Sample()

        @runtime_validation
        def foo(callback: typing.Optional[typing.Callable[[typing.Dict], typing.Any]]=None):
            return callback

        foo(None)
        with self.assertRaises(RuntimeTypeError):
            foo(s.method)

        with self.assertRaises(RuntimeTypeError):
            foo(s.method_bad)

        with self.assertRaises(RuntimeTypeError):
            foo(s)

        @runtime_validation
        def bar(callback: typing.Optional[typing.Callable[[typing.Any, typing.Dict], typing.Any]] = None):
            return callback

        bar(None)
        bar(s.method)

        with self.assertRaises(RuntimeTypeError):
            bar(s.method_bad)

        with self.assertRaises(RuntimeTypeError):
            bar(s)

        @runtime_validation
        def foo(callback: typing.Optional[typing.Callable[[typing.Any, typing.Dict], typing.Any]] = None):
            return callback

        sm = s.method

        print(1)
        print(sm.__enforcer__.callable_signature)
        print(2)
        print(dir(sm))
        try:
            print(sm.__mro__)
        except AttributeError:
            print('No MRO found.')

        try:
            print(sm.__call__)
        except AttributeError:
            print('No Call found.')

        foo(None)
        foo(s.method)

        with self.assertRaises(RuntimeTypeError):
            foo(s.method_bad)

        with self.assertRaises(RuntimeTypeError):
            foo(s)

    def test_class_init(self):
        """
        Verifies that an __init__ method of a class is correctly decorated and enforced
        """
        @runtime_validation
        class Foo:
            def __init__(self, fun: typing.Callable):
                self.fun = fun

        def bar(text):
            return text*2

        # Should not raise an error
        Foo(bar)

        with self.assertRaises(RuntimeTypeError):
            Foo(12)

        class Sample:
            @runtime_validation
            def __init__(self, fun: typing.Callable):
                self.fun = fun

        Sample(bar)

        with self.assertRaises(RuntimeTypeError):
            Sample(12)

    @runtime_validation
    def sample_function(self, text: str, data: typing.Union[int, None]) -> typing.Optional[int]:
        try:
            return int(text) + data
        except ValueError:
            if data is None:
                return None
            # Deliberate return type error
            return str(data)