import unittest
from unittest import skip
import typing

from enforce.utils import generic


class UtilsTests(unittest.TestCase):
    
    @skip
    def test_visiting(self):
        pass

    @skip
    def test_generics_creating(self):
        T = typing.TypeVar('T', int, str)
        class A(typing.Generic[T]):
            def __init__(self, data: T):
                prit('B')
                self.data = data

        a = A[int](2)
        print(a)
        print(a.__parameters__)
        self.assertEqual(a.data, 2)


if __name__ == '__main__':
    unittest.main()
