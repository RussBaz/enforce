import unittest
from typing import Iterator

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
            return iter([val for val in i])

        a = range(1, 10)
        ai = iter(a)

        foo(ai)

    def test_generator(self):
        """
        Verifies that Generator generic is respected
        """
        pass


if __name__ == "__name__":
    unittest.main()
