import unittest
from typing import Any, Callable

from enforce.enforcers import apply_enforcer, Enforcer


class EnforcerTests(unittest.TestCase):

    def setUp(self):
        def func_int___none(a: int) -> None: pass

        def func_int_empty___none(a: int, b) -> None: pass

        def func_int_empty___empty(a: int, b): pass

        def func_empty_int_empty___empty(a, b: int, c): pass

        def func_args_kwargs__empty(*args, **kwargs): pass

        def func_args__empty(*args): pass

        def func_empty_args__empty(a, *args): pass

        def func_any_args__none(a: Any, *args) -> None: pass

        self.func_int___none = func_int___none

        self.func_int_empty___none = func_int_empty___none
        self.func_int_empty___empty = func_int_empty___empty
        self.func_empty_int_empty___empty = func_empty_int_empty___empty

        self.func_args_kwargs__empty = func_args_kwargs__empty
        self.func_args__empty = func_args__empty
        self.func_empty_args__empty = func_empty_args__empty
        self.func_any_args__none = func_any_args__none

    def test_can_apply_enforcer(self):
        wrapped = apply_enforcer(self.func_int___none)
        enforcer = wrapped.__enforcer__
        self.assertTrue(isinstance(enforcer, Enforcer))

    def test_callable_simple_type(self):
        func_type = self.get_function_type(self.func_int___none)

        self.assertEquals(func_type, Callable[[int], None])

    def test_callable_missing_annotation(self):
        func_type = self.get_function_type(self.func_int_empty___none)

        self.assertEquals(func_type, Callable[[int, Any], None])

        func_type = self.get_function_type(self.func_int_empty___empty)

        self.assertEquals(func_type, Callable[[int, Any], Any])

        func_type = self.get_function_type(self.func_empty_int_empty___empty)

        self.assertEquals(func_type, Callable[[Any, int, Any], Any])

    def test_with_kwargs(self):
        func_type = self.get_function_type(self.func_args_kwargs__empty)

        self.assertEquals(func_type, Callable)

    def test_any_positional_only(self):
        func_type = self.get_function_type(self.func_args__empty)

        self.assertEquals(func_type, Callable)

    def test_any_extra_positional_only(self):
        func_type = self.get_function_type(self.func_empty_args__empty)

        self.assertEquals(func_type, Callable)

    def test_any_positional_with_return(self):
        func_type = self.get_function_type(self.func_any_args__none)

        self.assertEquals(func_type, Callable[..., None])

    def get_function_type(self, func):
        wrapped = apply_enforcer(func)
        enforcer = wrapped.__enforcer__
        func_type = enforcer.callable_signature
        return func_type


if __name__ == '__main__':
    unittest.main()
