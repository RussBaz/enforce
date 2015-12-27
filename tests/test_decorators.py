import unittest
from typing import Any, Optional, Sequence, TypeVar, Generic

import enforce
from enforce.exceptions import RuntimeTypeError


class DecoratorsTests(unittest.TestCase):
    """
    A container for decorator related tests
    """

    def test_docstring_and_name_presrved(self):
        """
        Verifies that an original name and a docstring are preserved
        """
        def test(text: str) -> None:
            """I am a docstring"""
            print(text)

        original_name = test.__name__
        original_doc = test.__doc__

        @enforce.runtime_validation
        def test(text: str) -> None:
            """I am a docstring"""
            print(text)

        self.assertEqual(original_doc, test.__doc__)
        self.assertEqual(original_name, test.__name__)

if __name__ == '__main__':
    unittest.main()
