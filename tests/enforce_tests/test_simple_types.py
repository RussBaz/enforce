import typing
import unittest

from enforce import runtime_validation, config
from enforce.exceptions import RuntimeTypeError


class SimpleTypesTests(unittest.TestCase):
    """
    Tests for the simple types which do not require special processing
    """

    def setUp(self):
        config(reset=True)

    def tearDown(self):
        config(reset=True)

    def test_any(self):
        @runtime_validation
        def sample(data: typing.Any) -> typing.Any:
            return data

        self.assertEqual(sample(100.3), 100.3)
        self.assertIsNone(sample(None))

        @runtime_validation
        def foo(a: typing.Any) -> typing.Any:
            return 10

        foo([10, 20])

        self.assertEqual(foo([10, 20]), 10)

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
            sample_bad("string")

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
            sample_bad("")

    def test_float(self):
        """
        Floats should accept only floats in invariant mode
        """

        @runtime_validation
        def sample(data: float) -> float:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> float:
            return data

        self.assertEqual(sample(1.0), 1.0)
        with self.assertRaises(RuntimeTypeError):
            sample(1)
        with self.assertRaises(RuntimeTypeError):
            sample("")

        with self.assertRaises(RuntimeTypeError):
            sample_bad("")

        config({"mode": "covariant"})
        sample(1)

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

        self.assertEqual(sample(1 + 1j), 1 + 1j)
        self.assertEqual(sample(1), 1)
        self.assertEqual(sample(1.0), 1.0)
        with self.assertRaises(RuntimeTypeError):
            sample("")

        with self.assertRaises(RuntimeTypeError):
            sample_bad("")

    def test_string(self):
        @runtime_validation
        def sample(data: str) -> str:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> str:
            return data

        self.assertEqual(sample(""), "")
        with self.assertRaises(RuntimeTypeError):
            sample(1)

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1)

    def test_bytes(self):
        """
        Bytes should accept bytes as well bytearray and memorieview
        """

        @runtime_validation
        def sample(data: bytes) -> bytes:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> bytes:
            return data

        self.assertEqual(sample(b""), b"")
        self.assertEqual(sample(bytearray(2)), bytearray(2))
        self.assertEqual(sample(memoryview(b"")), memoryview(b""))
        with self.assertRaises(RuntimeTypeError):
            sample("")

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
            sample(b"")

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1)

    def test_memoryview(self):
        @runtime_validation
        def sample(data: memoryview) -> memoryview:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> memoryview:
            return data

        self.assertEqual(sample(memoryview(b"")), memoryview(b""))
        with self.assertRaises(RuntimeTypeError):
            sample(b"")

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1)


if __name__ == "__name__":
    unittest.main()
