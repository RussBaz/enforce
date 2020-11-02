import typing
import unittest

from enforce import runtime_validation
from enforce.exceptions import RuntimeTypeError


class SetTypesTests(unittest.TestCase):
    def test_basic_set(self):
        @runtime_validation
        def sample_func(data: typing.Set[str]) -> typing.Set[int]:
            return set(int(item) for item in data)

        sample_func({"1", "2"})

        with self.assertRaises(RuntimeTypeError):
            sample_func(["1", "2"])

        with self.assertRaises(RuntimeTypeError):
            sample_func({"1", 1})


if __name__ == "__name__":
    unittest.main()
