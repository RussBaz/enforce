import unittest
from typing import Iterator, Iterable, Generator

from enforce import runtime_validation


class IterableTypesTests(unittest.TestCase):
    """
    Tests for iterator and generator support
    """

    def test_iterator(self):
        """
        Verifies that Iterator generic is respected
        """
        @runtime_validation
        def foo(i: Iterator[int]):
            result = []
            for val in i:
                result.append(val)

            return iter(result)

        a = range(1, 10)
        ai = iter(a)

        foo(ai)

    def test_generator(self):
        """
        Verifies that Generator generic is respected
        """
        pass
