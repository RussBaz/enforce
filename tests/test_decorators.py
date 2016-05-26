import unittest
import typing

import enforce
from enforce import runtime_validation
from enforce.exceptions import RuntimeTypeError, EnforceConfigurationError


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

        # Lambda cannot be annotated with type hints
        # Hence, it cannot be more specific than typing.Callable
        # func = lambda x: str(x)

        def bar(data: int) -> str:
            return str(data)

        foo(bar, 5)

        with self.assertRaises(RuntimeTypeError):
            foo(5, 7)

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

        good = (1, 2)
        bad = 1

        test(good)

        with self.assertRaises(RuntimeTypeError):
            test(bad)


class DecoratorArgumentsTests(unittest.TestCase):

    def test_config_validation(self):
        with self.assertRaises(EnforceConfigurationError):
            @enforce.runtime_validation(recursion_limit='a')
            def foo1(a: typing.Any) -> typing.Any: return a

        with self.assertRaises(EnforceConfigurationError):
            @enforce.runtime_validation(recursion_limit=-5)
            def foo2(a: typing.Any) -> typing.Any: return a

        with self.assertRaises(EnforceConfigurationError):
            @enforce.runtime_validation(iterable_size=-5)
            def foo3(a: typing.Any) -> typing.Any: return a

        with self.assertRaises(EnforceConfigurationError):
            @enforce.runtime_validation(iterable_size='a')
            def foo4(a: typing.Any) -> typing.Any: return a

        with self.assertRaises(EnforceConfigurationError):
            @enforce.runtime_validation(group=5)
            def foo5(a: typing.Any) -> typing.Any: return a

        with self.assertRaises(EnforceConfigurationError):
            @enforce.runtime_validation(enable=5)
            def foo6(a: typing.Any) -> typing.Any: return a

    def test_basic_arguments(self):
        @enforce.runtime_validation
        def test1(foo: typing.Any): return foo

        @enforce.runtime_validation(recursion_limit=5, iterable_size='first', group='foo', enable=True)
        def test2(foo: typing.Any): return foo

        test1(5)
        test2(5)

    def test_enable(self):
        @runtime_validation(enable=True)
        def test1(a: typing.List[str]): return a

        @runtime_validation(enable=False)
        def test2(a: typing.List[str]): return a

        with self.assertRaises(RuntimeTypeError):
            test1(5)

        # This should work with that decorator disabled
        test2(5)

    def test_groups(self):
        """ TODO: This """
        enforce.config(enable=False)
        enforce.set_group('foo', True)

        @runtime_validation(group='foo')
        def test1(a: typing.List[str]): return a

        @runtime_validation(group='foo')
        def test2(a: typing.List[str]): return a

        @runtime_validation(group='bar')
        def test3(a: typing.List[str]): return a

        with self.assertRaises(RuntimeTypeError):
            test1(5)

        with self.assertRaises(RuntimeTypeError):
            test2(5)

        test3(5)

        enforce.config(enable=True)

    def test_global_enable(self):
        enforce.config(enable=False)

        @runtime_validation
        def test1(a: typing.List[str]): return a

        @runtime_validation(enable=True)
        def test2(a: typing.List[str]): return a

        @runtime_validation(enable=False)
        def test3(a: typing.List[str]): return a

        try:
            test1(5)  # Should work with disabled

            with self.assertRaises(RuntimeTypeError):
                test2(5)

            test3(5)  # Should work with disabled
        except:
            # NEED TO RE-ENABLE
            enforce.config(enable=True)
            raise
        enforce.config(enable=True)


if __name__ == '__main__':
    unittest.main()
