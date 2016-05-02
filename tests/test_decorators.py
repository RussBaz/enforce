import unittest
import typing

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
        @runtime_validation
        class SampleClass:
            def test(self, data: int) -> int:
                return data

            def test_bad(self, data: typing.Any) -> int:
                return data

        sample = SampleClass()
        self.assertEqual(sample.test(1), 1)
        self.assertEqual(sample.test_bad(1), 1)

        with self.assertRaises(RuntimeTypeError):
            sample.test('')

        with self.assertRaises(RuntimeTypeError):
            sample.test_bad('')

    def test_method(self):
        """
        Checks if a method of a class object can be decorated
        """
        class SampleClass:
            @runtime_validation
            def test(self, data: int) -> int:
                return data

            @runtime_validation
            def test_bad(self, data: typing.Any) -> int:
                return data

        sample = SampleClass()
        self.assertEqual(sample.test(1), 1)
        self.assertEqual(sample.test_bad(1), 1)

        with self.assertRaises(RuntimeTypeError):
            sample.test('')

        with self.assertRaises(RuntimeTypeError):
            sample.test_bad('')

    def test_staticmethod(self):
        """
        Checks if a staticmethod of a class object can be decorated
        """
        class SampleClass:
            @runtime_validation
            @staticmethod
            def test(data: int) -> int:
                return data

            @staticmethod
            @runtime_validation
            def test2(data: int) -> int:
                return data

            @runtime_validation
            @staticmethod
            def test_bad(data: typing.Any) -> int:
                return data

            @staticmethod
            @runtime_validation
            def test_bad2(data: typing.Any) -> int:
                return data

        sample = SampleClass()
        self.assertEqual(sample.test(1), 1)
        self.assertEqual(sample.test2(1), 1)
        self.assertEqual(sample.test_bad(1), 1)
        self.assertEqual(sample.test_bad2(1), 1)

        self.assertEqual(SampleClass.test(1), 1)
        self.assertEqual(SampleClass.test2(1), 1)
        self.assertEqual(SampleClass.test_bad(1), 1)
        self.assertEqual(SampleClass.test_bad2(1), 1)

        with self.assertRaises(RuntimeTypeError):
            sample.test('')

        with self.assertRaises(RuntimeTypeError):
            sample.test2('')

        with self.assertRaises(RuntimeTypeError):
            sample.test_bad('')

        with self.assertRaises(RuntimeTypeError):
            sample.test_bad2('')

        with self.assertRaises(RuntimeTypeError):
            SampleClass.test('')

        with self.assertRaises(RuntimeTypeError):
            SampleClass.test2('')

        with self.assertRaises(RuntimeTypeError):
            SampleClass.test_bad('')

        with self.assertRaises(RuntimeTypeError):
            SampleClass.test_bad2('')

    def test_classmethod(self):
        """
        Checks if a classmethod of a class object can be decorated
        """
        class SampleClass:
            @runtime_validation
            @classmethod
            def test(cls, data: int) -> int:
                return data

            @classmethod
            @runtime_validation
            def test2(cls, data: int) -> int:
                return data

            @runtime_validation
            @classmethod
            def test_bad(cls, data: typing.Any) -> int:
                return data

            @classmethod
            @runtime_validation
            def test_bad2(cls, data: typing.Any) -> int:
                return data

        sample = SampleClass()
        self.assertEqual(sample.test(1), 1)
        self.assertEqual(sample.test2(1), 1)
        self.assertEqual(sample.test_bad(1), 1)
        self.assertEqual(sample.test_bad2(1), 1)

        self.assertEqual(SampleClass.test(1), 1)
        self.assertEqual(SampleClass.test2(1), 1)
        self.assertEqual(SampleClass.test_bad(1), 1)
        self.assertEqual(SampleClass.test_bad2(1), 1)

        #with self.assertRaises(RuntimeTypeError):
        #    sample.test('')

        with self.assertRaises(RuntimeTypeError):
            sample.test2('')

        #with self.assertRaises(RuntimeTypeError):
        #    sample.test_bad('')

        with self.assertRaises(RuntimeTypeError):
            sample.test_bad2('')

        #with self.assertRaises(RuntimeTypeError):
        #    SampleClass.test('')

        with self.assertRaises(RuntimeTypeError):
            SampleClass.test2('')

        #with self.assertRaises(RuntimeTypeError):
        #    SampleClass.test_bad('')

        with self.assertRaises(RuntimeTypeError):
            SampleClass.test_bad2('')

    @unittest.skip
    def test_isntance(self):
        """
        Checks if an instance method can be decorated
        """
        pass

    def test_working_callable_argument(self):
        @enforce.runtime_validation
        def foo(func: typing.Callable[[int], str], bar: int) -> str:
            return func(bar)

        foo(lambda x: str(x), 5)

        try:
            foo(5, 7)
        except enforce.exceptions.RuntimeTypeError:
            pass

    def test_tuple_support(self):
        @enforce.runtime_validation
        def test(tup: typing.Tuple[int, str, float]) -> typing.Tuple[str, int]:
            return tup[1], tup[0]

        tup = ('a', 5, 3.0)
        try:
            test(tup)
            raise AssertionError('RuntimeTypeError should have been raised')
        except enforce.exceptions.RuntimeTypeError:
            pass

    def test_list_support(self):
        @enforce.runtime_validation
        def test(arr: typing.List[str]) -> typing.List[str]:
            return arr[:1]

        arr = [1, 'b', 'c']
        try:
            test(arr)
            raise AssertionError('RuntimeTypeError should have been raised')
        except enforce.exceptions.RuntimeTypeError:
            pass

    def test_dict_support(self):
        @enforce.runtime_validation
        def test(hash: typing.Dict[str, int]) -> typing.Dict[int, str]:
            return {value: key for key, value in hash.items()}

        hash = {5: 1, 'b': 5}
        try:
            test(hash)
            raise AssertionError('RuntimeTypeError should have been raised')
        except enforce.exceptions.RuntimeTypeError:
            pass

    def test_recursion_slim(self):
        @enforce.runtime_validation
        def test(tup: typing.Tuple) -> typing.Tuple:
            return tup

        tup = (1, 2)
        try:
            test(tup)
            raise AssertionError('RuntimeTypeError should have been raised')
        except enforce.exceptions.RuntimeTypeError:
            pass




if __name__ == '__main__':
    unittest.main()
