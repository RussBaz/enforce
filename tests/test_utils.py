import unittest
from unittest import skip
import typing

from enforce.utils import generic


class UtilsTests(unittest.TestCase):
    
    @skip
    def test_visiting(self):
        pass

    def test_generics_creating(self):
        T = typing.TypeVar('T', int, str)
        class A(typing.Generic[T]):
            def __init__(self, data: T):
                print('B')
                self.data = data

        B = generic(A[int])
        a = B(2)
        print(A)
        print(A.__parameters__)
        print(A[int])
        print(A[int].__parameters__)
        print(B)
        print(B.__parameters__)
        print(a)
        print(a.__parameters__)
        self.assertEqual(a.data, 2)


if __name__ == '__main__':
    unittest.main()
