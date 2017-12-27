import typing
import unittest

from enforce import runtime_validation
from enforce.exceptions import RuntimeTypeError


class GenericTypesTests(unittest.TestCase):
    """
    Tests for the generic types
    """

    def test_custom_generic_initialisation(self):
        """
        Verifies that user defined generics can be initialised
        """
        T = typing.TypeVar('T')

        class Sample(typing.Generic[T]):
            pass

        SD = runtime_validation(Sample)

        ST = Sample[int]
        SDT = SD[int]

        s = Sample()
        sd = SD()
        st = ST()
        sdt = SDT()

        self.assertFalse(hasattr(s, '__enforcer__'))
        self.assertFalse(hasattr(st, '__enforcer__'))
        self.assertTrue(hasattr(sd, '__enforcer__'))
        self.assertTrue(hasattr(sdt, '__enforcer__'))

        self.assertEqual(sd.__enforcer__.signature, Sample)
        self.assertEqual(sdt.__enforcer__.signature, Sample)

        self.assertEqual(sd.__enforcer__.generic, SD.__enforcer__.generic)
        self.assertEqual(sdt.__enforcer__.generic, SDT.__enforcer__.generic)

        self.assertEqual(sd.__enforcer__.bound, SD.__enforcer__.bound)
        self.assertEqual(sdt.__enforcer__.bound, SDT.__enforcer__.bound)

        for hint_name, hint_value in sdt.__enforcer__.hints.items():
            self.assertEqual(hint_value, SDT.__enforcer__.hints[hint_name])

        self.assertEqual(len(sdt.__enforcer__.hints), len(SDT.__enforcer__.hints))

    def test_custom_generic_validation(self):
        """
        Verifies that user defined generic can be used as a type hint
        """
        T = typing.TypeVar('T')

        @runtime_validation
        class Sample(typing.Generic[T]):
            def get(self, data: T) -> T:
                return data

        @runtime_validation
        def return_int(data: Sample[int], arg: int) -> int:
            return data.get(arg)

        @runtime_validation
        def return_any(data: Sample) -> typing.Any:
            return data

        good = Sample[int]()
        bad = Sample[str]()
        other = Sample()
        strange = Sample[T]()

        self.assertEqual(return_int(good, 1), 1)
        self.assertIs(return_any(other), other)

        # TODO: Find out exactly what should be be happening in this case
        # self.assertIs(return_any(strange), strange)

        with self.assertRaises(RuntimeTypeError):
            return_int(bad, 1)

        with self.assertRaises(RuntimeTypeError):
            return_int(other, 1)

        with self.assertRaises(RuntimeTypeError):
            return_int(strange, 1)

        with self.assertRaises(RuntimeTypeError):
            return_any(good)

        with self.assertRaises(RuntimeTypeError):
            return_any(bad)