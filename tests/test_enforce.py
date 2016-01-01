import typing
import unittest

from enforce import runtime_validation
from enforce.exceptions import RuntimeTypeError


class GeneralTests(unittest.TestCase):
    """
    A container for general tests
    """

    def test_argument_validation(self):
        self.assertEqual(self.sample_function('11', 1), 12)

        result = 0
        with self.assertRaises(RuntimeTypeError):
            result += self.sample_function(1, 2)

        self.assertEqual(result, 0)

    def test_return_value_validation(self):
        self.assertIsNone(self.sample_function('', None))

        result = 0
        with self.assertRaises(RuntimeTypeError):
            result += self.sample_function('', 1)

        self.assertEqual(result, 0)

    def test_class_decorator(self):
        class SampleClass:
            def test(self, data: int) -> int:
                return data

        sample = SampleClass()
        self.assertEqual(sample.test(1), 1)

        SampleClass = runtime_validation(SampleClass)
        sample = SampleClass()
        self.assertEqual(sample.test(1), 1)

        with self.assertRaises(RuntimeTypeError):
            sample.test('')

    @runtime_validation
    def sample_function(self, text: str, data: typing.Union[int, None]) -> typing.Optional[int]:
        try:
            return int(text) + data
        except ValueError:
            if data is None:
                return None
            # Deliberate return type error
            return str(data)


class SimpleTypesTests(unittest.TestCase):
    """
    Tests for the simple types which do not require special processing
    """

    def test_any(self):
        @runtime_validation
        def sample(data: typing.Any) -> typing.Any:
            return data

        self.assertEqual(sample(100.3), 100.3)
        self.assertIsNone(sample(None))

    def test_none(self):
        @runtime_validation
        def sample(data: None) -> None:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> None:
            return data

        self.assertIsNone(sample(None))
        with self.assertRaises(RuntimeTypeError):
            sample_bad(1)

    def test_bool(self):
        @runtime_validation
        def sample(data: bool) -> bool:
            return not data

        @runtime_validation
        def sample_bad(data: typing.Any) -> bool:
            return data

        self.assertFalse(sample(True))
        with self.assertRaises(RuntimeTypeError):
            sample(1)

        with self.assertRaises(RuntimeTypeError):
            sample_bad('string')

    def test_int(self):
        @runtime_validation
        def sample(data: int) -> int:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> int:
            return data

        self.assertEqual(sample(1), 1)
        with self.assertRaises(RuntimeTypeError):
            sample(1.0)

        with self.assertRaises(RuntimeTypeError):
            sample_bad('')

    def test_float(self):
        """
        Floats should accept both floats and integers
        """
        @runtime_validation
        def sample(data: float) -> float:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> float:
            return data

        self.assertEqual(sample(1.0), 1.0)
        self.assertEqual(sample(1), 1)
        with self.assertRaises(RuntimeTypeError):
            sample('')

        with self.assertRaises(RuntimeTypeError):
            sample_bad('')

    def test_complex(self):
        """
        Complex numbers should accept complex, integers and floats
        """
        @runtime_validation
        def sample(data: complex) -> complex:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> complex:
            return data

        self.assertEqual(sample(1+1j), 1+1j)
        self.assertEqual(sample(1), 1)
        self.assertEqual(sample(1.0), 1.0)
        with self.assertRaises(RuntimeTypeError):
            sample('')

        with self.assertRaises(RuntimeTypeError):
            sample_bad('')

    def test_string(self):
        @runtime_validation
        def sample(data: str) -> str:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> str:
            return data

        self.assertEqual(sample(''), '')
        with self.assertRaises(RuntimeTypeError):
            sample(1)

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1)

    def test_bytes(self):
        """
        BYtes should accept bytes as well bytearray and memorieview
        """
        @runtime_validation
        def sample(data: bytes) -> bytes:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> bytes:
            return data

        self.assertEqual(sample(b''), b'')
        self.assertEqual(sample(bytearray(2)), bytearray(2))
        self.assertEqual(sample(memoryview(b'')), memoryview(b''))
        with self.assertRaises(RuntimeTypeError):
            sample('')

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1)

    def test_bytearray(self):
        @runtime_validation
        def sample(data: bytearray) -> bytearray:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> bytearray:
            return data

        self.assertEqual(sample(bytearray(2)), bytearray(2))
        with self.assertRaises(RuntimeTypeError):
            sample(b'')

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1)

    def test_memoryview(self):
        @runtime_validation
        def sample(data: memoryview) -> memoryview:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> memoryview:
            return data

        self.assertEqual(sample(memoryview(b'')), memoryview(b''))
        with self.assertRaises(RuntimeTypeError):
            sample(b'')

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1)


class ComplextTypesTests(unittest.TestCase):
    """
    Tests for the simple types which require special processing
    """

    def test_union(self):
        @runtime_validation
        def sample(data: typing.Union[int, str]) -> typing.Union[int, str]:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> typing.Union[int, str]:
            return data

        self.assertEqual(sample(1), 1)
        self.assertEqual(sample(''), '')
        with self.assertRaises(RuntimeTypeError):
            sample(b'')

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1.0)

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
            sample('')

        with self.assertRaises(RuntimeTypeError):
            sample_bad('')

    def test_tuple(self):
        @runtime_validation
        def sample(data: typing.Tuple[int, str]) -> typing.Tuple[int, str]:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> typing.Tuple[int, str]:
            return data

        self.assertEqual(sample((1, '')), (1, ''))
        with self.assertRaises(RuntimeTypeError):
            sample((1, 1))

        with self.assertRaises(RuntimeTypeError):
            sample(())

        with self.assertRaises(RuntimeTypeError):
            sample([])

        with self.assertRaises(RuntimeTypeError):
            sample_bad((''))

    def test_simple_unbounded_type_var(self):
        A = typing.TypeVar('A')

        @runtime_validation
        def sample(data: A) -> A:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any, option: A) -> A:
            return data

        self.assertEqual(sample(1), 1)
        self.assertEqual(sample_bad('', 'hello world'), '')

        with self.assertRaises(RuntimeTypeError):
            sample_bad('', 1)

    def test_simple_bounded_type_var(self):
        A = typing.TypeVar('A', int, str)

        @runtime_validation
        def sample(data: A) -> A:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> A:
            return data

        self.assertEqual(sample(1), 1)
        self.assertEqual(sample(''), '')
        self.assertEqual(sample_bad(1), 1)
        self.assertEqual(sample_bad(''), '')

        with self.assertRaises(RuntimeTypeError):
            sample(1.0)

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1.0)


class ContainerTypesTests(unittest.TestCase):
    """
    Tests for the container types - types of unbounded size
    """
    pass


class IterableTypesTests(unittest.TestCase):
    """
    Tests for iterator and generator support
    """
    pass


class CallableTypesTests(unittest.TestCase):
    """
    Tests for the callable types such as functions
    """
    pass


class GenericTypesTests(unittest.TestCase):
    """
    Tests for the generic types
    """
    
    def test_custom_generic(self):
        T = typing.TypeVar('T')
        class Sample(typing.Generic[T]):
            def get(self, data: T) -> T:
                return data

        @runtime_validation
        def return_int(data: Sample[int], arg: int) -> int:
            return data.get(arg)

        good = Sample[int]()
        bad = Sample[str]()
        #other = Sample()
        #strange = Sample[T]()

        #print('t:', type(good))
        #print('t:', type(bad))
        #print('t:', type(other))

        #print(issubclass(type(good), Sample[int]))
        #print(issubclass(type(good), typing.Generic))

        self.assertEqual(return_int(good, 1), 1)

        with self.assertRaises(RuntimeTypeError):
            return_int(bad, 1)


class NestedTypesTests(unittest.TestCase):
    """
    Tests for special and corner cases when types are deeply nested
    """
    pass


if __name__ == '__main__':
    unittest.main()
