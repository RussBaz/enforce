import unittest

from enforce import runtime_validation
from enforce.exceptions import RuntimeTypeError


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

        test = runtime_validation(test)

        self.assertEqual(original_doc, test.__doc__)
        self.assertEqual(original_name, test.__name__)

    def test_class(self):
        """
        Checks if a class object can be decorated
        """
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

    def test_method(self):
        """
        Checks if a method of a class object can be decorated
        """
        class SampleClass:
            @runtime_validation
            def test(self, data: int) -> int:
                return data

        sample = SampleClass()
        self.assertEqual(sample.test(1), 1)

        with self.assertRaises(RuntimeTypeError):
            sample.test('')

    @unittest.skip
    def test_staticmethod(self):
        """
        Checks if a staticmethod of a class object can be decorated
        """
        pass

    @unittest.skip
    def test_clasmethod(self):
        """
        Checks if a classmethod of a class object can be decorated
        """
        pass

    @unittest.skip
    def test_isntance(self):
        """
        Checks if an instance method can be decorated
        """
        pass

if __name__ == '__main__':
    unittest.main()
