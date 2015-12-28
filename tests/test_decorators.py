import unittest

import enforce


class DecoratorsTests(unittest.TestCase):
    """
    A container for decorator related tests
    """

    def test_docstring_name_presrved(self):
        """
        Verifies that an original name and a docstring are preserved
        """
        def test(text: str) -> None:
            """I am a docstring"""
            print(text)

        original_name = test.__name__
        original_doc = test.__doc__

        test = enforce.runtime_validation(test)

        self.assertEqual(original_doc, test.__doc__)
        self.assertEqual(original_name, test.__name__)

if __name__ == '__main__':
    unittest.main()
