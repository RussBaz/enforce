import typing
import unittest

from enforce import runtime_validation, config
from enforce.exceptions import RuntimeTypeError


class TestDecorators(unittest.TestCase):
    """
    A container for decorator related tests
    """

    def test_docstring_name_preserved(self):
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
        class SampleClass(object):
            def test(self, data: int) -> int:
                return data

            def test_bad(self, data: typing.Any) -> int:
                return data

        sample = SampleClass()
        self.assertEqual(sample.test(1), 1)
        self.assertEqual(sample.test_bad(1), 1)

        with self.assertRaises(RuntimeTypeError):
            sample.test("")

        with self.assertRaises(RuntimeTypeError):
            sample.test_bad("")

    def test_method(self):
        """
        Checks if a method of a class object can be decorated
        """

        class SampleClass(object):
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
            sample.test("")

        with self.assertRaises(RuntimeTypeError):
            sample.test_bad("")

    def test_staticmethod(self):
        """
        Checks if a staticmethod of a class object can be decorated
        """

        class SampleClass(object):
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
            sample.test("")

        with self.assertRaises(RuntimeTypeError):
            sample.test2("")

        with self.assertRaises(RuntimeTypeError):
            sample.test_bad("")

        with self.assertRaises(RuntimeTypeError):
            sample.test_bad2("")

        with self.assertRaises(RuntimeTypeError):
            SampleClass.test("")

        with self.assertRaises(RuntimeTypeError):
            SampleClass.test2("")

        with self.assertRaises(RuntimeTypeError):
            SampleClass.test_bad("")

        with self.assertRaises(RuntimeTypeError):
            SampleClass.test_bad2("")

            # testing staticmethods with class decorator

        @runtime_validation
        class Foo(object):
            @staticmethod
            def good(x: int) -> int:
                return x

            @staticmethod
            def bad(x: int) -> int:
                return str(x)

        self.assertEqual(Foo.good(1), 1)
        self.assertEqual(Foo.good(5), 5)

        with self.assertRaises(RuntimeTypeError):
            Foo.bad(5)

    def test_classmethod(self):
        """
        Checks if a classmethod of a class object can be decorated
        """

        class SampleClass(object):
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

        # with self.assertRaises(RuntimeTypeError):
        #    sample.test('')

        with self.assertRaises(RuntimeTypeError):
            sample.test2("")

        # with self.assertRaises(RuntimeTypeError):
        #    sample.test_bad('')

        with self.assertRaises(RuntimeTypeError):
            sample.test_bad2("")

        # with self.assertRaises(RuntimeTypeError):
        #    SampleClass.test('')

        with self.assertRaises(RuntimeTypeError):
            SampleClass.test2("")

        # with self.assertRaises(RuntimeTypeError):
        #    SampleClass.test_bad('')

        with self.assertRaises(RuntimeTypeError):
            SampleClass.test_bad2("")

    def test_property(self):
        """
        Checks if property object can be type checked
        """

        @runtime_validation
        class Sample(object):
            def __init__(self):
                self._x = 0

            @property
            def x(self):
                return self._x

            @x.setter
            def x(self, value: int):
                self._x = value

        class Sample2(object):
            def __init__(self):
                self._x = 0

            @property
            def x(self):
                return self._x

            @runtime_validation
            @x.setter
            def x(self, value: int):
                self._x = value

        class Sample3(object):
            def __init__(self):
                self._x = 0

            @runtime_validation
            @property
            def x(self):
                return self._x

            @x.setter
            @runtime_validation
            def x(self, value: int):
                self._x = value

        s = Sample()
        s2 = Sample2()
        s3 = Sample3()

        self.assertEqual(0, s.x)
        self.assertEqual(0, s2.x)
        self.assertEqual(0, s3.x)

        s.x = 1
        s2.x = 1
        s3.x = 1

        self.assertEqual(1, s.x)
        self.assertEqual(1, s2.x)
        self.assertEqual(1, s3.x)

        with self.assertRaises(RuntimeTypeError):
            s.x = "string"

        with self.assertRaises(RuntimeTypeError):
            s2.x = "string"

        with self.assertRaises(RuntimeTypeError):
            s3.x = "string"

        self.assertEqual(1, s.x)
        self.assertEqual(1, s2.x)
        self.assertEqual(1, s3.x)

    def test_working_callable_argument(self):
        @runtime_validation
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
        @runtime_validation
        def test(tup: typing.Tuple[int, str, float]) -> typing.Tuple[str, int]:
            return tup[1], tup[0]

        tup = ("a", 5, 3.0)

        with self.assertRaises(RuntimeTypeError):
            test(tup)

    def test_list_support(self):
        @runtime_validation
        def test(arr: typing.List[str]) -> typing.List[str]:
            return arr[:1]

        arr = [1, "b", "c"]

        with self.assertRaises(RuntimeTypeError):
            test(arr)

    def test_dict_support(self):
        @runtime_validation
        def test(hash_values: typing.Dict[str, int]) -> typing.Dict[int, str]:
            return {value: key for key, value in hash_values.items()}

        hash_values = {5: 1, "b": 5}
        with self.assertRaises(RuntimeTypeError):
            test(hash_values)

    def test_recursion_slim(self):
        @runtime_validation
        def test(tup: typing.Tuple) -> typing.Tuple:
            return tup

        good = (1, 2)
        bad = 1

        test(good)

        with self.assertRaises(RuntimeTypeError):
            test(bad)


class TestDecoratorArguments(unittest.TestCase):
    def setUp(self):
        config({"enabled": True})

    def tearDown(self):
        config({"enabled": True})

    def test_config_validation(self):
        """
        If the unsupported value for the config option is provided,
        A TypeError should be thrown
        """
        with self.assertRaises(TypeError):

            @runtime_validation(group=5)
            def foo5(a: typing.Any) -> typing.Any:
                return a

        with self.assertRaises(TypeError):

            @runtime_validation(enabled=5)
            def foo6(a: typing.Any) -> typing.Any:
                return a

    def test_basic_arguments(self):
        @runtime_validation
        def test1(foo: typing.Any):
            return foo

        @runtime_validation(group="foo", enabled=True)
        def test2(foo: typing.Any):
            return foo

        test1(5)
        test2(5)

    def test_enable(self):
        @runtime_validation(enabled=True)
        def test1(a: typing.List[str]):
            return a

        @runtime_validation(enabled=False)
        def test2(a: typing.List[str]):
            return a

        with self.assertRaises(RuntimeTypeError):
            test1(5)

        # This should work with that decorator disabled
        test2(5)

    def test_groups(self):
        config(
            {
                "enabled": None,
                "groups": {
                    "set": {"foo": True},
                    "disable_previous": True,
                    "default": False,
                },
            }
        )

        @runtime_validation(group="foo")
        def test1(a: typing.List[str]):
            return a

        @runtime_validation(group="foo", enabled=True)
        def test2(a: typing.List[str]):
            return a

        @runtime_validation(group="bar")
        def test3(a: typing.List[str]):
            return a

        @runtime_validation(group="bar", enabled=True)
        def test4(a: typing.List[str]):
            return a

        @runtime_validation(group="foo", enabled=False)
        def test5(a: typing.List[str]):
            return a

        with self.assertRaises(RuntimeTypeError):
            test1(5)

        with self.assertRaises(RuntimeTypeError):
            test2(5)

        test3(5)

        with self.assertRaises(RuntimeTypeError):
            test4(5)

        test5(5)

        config({"groups": {"set": {"foo": False}}})

        test1(5)

        with self.assertRaises(RuntimeTypeError):
            test2(5)

    def test_global_enable(self):
        config({"enabled": False})

        @runtime_validation
        def test1(a: typing.List[str]):
            return a

        @runtime_validation(enabled=True)
        def test2(a: typing.List[str]):
            return a

        @runtime_validation(enabled=False)
        def test3(a: typing.List[str]):
            return a

        test1(5)
        test2(5)
        test3(5)

        config({"enabled": True})

        with self.assertRaises(RuntimeTypeError):
            test1(5)

        with self.assertRaises(RuntimeTypeError):
            test2(5)

        test3(5)


if __name__ == "__main__":
    unittest.main()
