import unittest
from typing import Any, Callable, TypeVar, Generic

from enforce.enforcers import apply_enforcer, Enforcer, GenericProxy


class EnforcerTests(unittest.TestCase):

    def setUp(self):
        """
        Because functions are recreated on every pass, it is guaranteed to remain unmodified
        """
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

        self.assertEqual(func_type, Callable[[int], None])

    def test_callable_missing_annotation(self):
        func_type = self.get_function_type(self.func_int_empty___none)

        self.assertEqual(func_type, Callable[[int, Any], None])

        func_type = self.get_function_type(self.func_int_empty___empty)

        self.assertEqual(func_type, Callable[[int, Any], Any])

        func_type = self.get_function_type(self.func_empty_int_empty___empty)

        self.assertEqual(func_type, Callable[[Any, int, Any], Any])

    def test_with_kwargs(self):
        func_type = self.get_function_type(self.func_args_kwargs__empty)

        self.assertEqual(func_type, Callable)

    def test_any_positional_only(self):
        func_type = self.get_function_type(self.func_args__empty)

        self.assertEqual(func_type, Callable)

    def test_any_extra_positional_only(self):
        func_type = self.get_function_type(self.func_empty_args__empty)

        self.assertEqual(func_type, Callable)

    def test_any_positional_with_return(self):
        func_type = self.get_function_type(self.func_any_args__none)

        self.assertEqual(func_type, Callable[..., None])

    def get_function_type(self, func):
        wrapped = apply_enforcer(func)
        enforcer = wrapped.__enforcer__
        func_type = enforcer.callable_signature
        return func_type


class GenericProxyTests(unittest.TestCase):

    def test_can_proxy_generic(self):
        """
        Verifies that Generic Proxy wraps the original user defined generic
        and applies an enforcer to it
        """
        T = TypeVar('T')
        K = TypeVar('K')
        V = TypeVar('V')

        class AG(Generic[T]):
            pass

        class BG(Generic[T, K, V]):
            pass

        AP = GenericProxy(AG)
        BP = GenericProxy(BG)

        self.assertIs(AP.__class__, AG.__class__)
        self.assertIs(BP.__class__, BG.__class__)

        self.assertIs(AP.__wrapped__, AG)
        self.assertIs(BP.__wrapped__, BG)

        self.assertTrue(AP.__enforcer__.generic)
        self.assertTrue(BP.__enforcer__.generic)

        self.assertFalse(AP.__enforcer__.bound)
        self.assertFalse(BP.__enforcer__.bound)
        
        self.assertFalse(hasattr(AG, '__enforcer__'))
        self.assertFalse(hasattr(BG, '__enforcer__'))

    def test_typed_generic_is_proxied(self):
        """
        Verifies that when Generic Proxy is constrained, the returned generic is also wrapped in a Generic Proxy
        And its origin property is pointing to a parent Generic Proxy (not an original user defined generic)
        """
        types = (int, int, str)

        T = TypeVar('T')
        K = TypeVar('K')
        V = TypeVar('V')

        T_t, K_t, V_t = types

        class AG(Generic[T, K, V]):
            pass

        AP = GenericProxy(AG)

        AGT = AG[T_t, K_t, V_t]
        APT = AP[T_t, K_t, V_t]

        self.assertFalse(hasattr(AGT, '__enforcer__'))

        self.assertTrue(APT.__enforcer__.generic)
        self.assertTrue(APT.__enforcer__.bound)
        self.assertIs(APT.__origin__, AG)

        self.assertEqual(len(APT.__args__), len(types))
        for i, arg in enumerate(APT.__args__):
            self.assertIs(arg, types[i])

    def test_can_init_proxied_generics(self):
        """
        Verifies that all proxied generics can be instantiated
        """
        T = TypeVar('T')

        class AG(Generic[T]):
            pass

        AP = GenericProxy(AG)
        APT = AP[int]

        ap = AP()
        apt = APT()

    def test_cannot_apply_to_non_generics(self):
        """
        Verifies that a Generic Proxy can only be applied to valid generics
        Otherwise, it should return a type error.
        """
        T = TypeVar('T')

        class AG(Generic[T]):
            pass

        class B(AG):
            pass

        AP = GenericProxy(AG)
        APT = AP[int]

        ag = AG()
        agt = AG[int]()
        ap = AP()
        apt = APT()

        with self.assertRaises(TypeError):
            GenericProxy(ag)

        with self.assertRaises(TypeError):
            GenericProxy(agt)

        with self.assertRaises(TypeError):
            GenericProxy(ap)

        with self.assertRaises(TypeError):
            GenericProxy(apt)

        with self.assertRaises(TypeError):
            GenericProxy(B)

    def test_instances_have_enforcer(self):
        """
        Verifies that instances of generics wrapped with Generic Proxy have __enforcer__ object
        """
        T = TypeVar('T')

        class AG(Generic[T]):
            pass

        AP = GenericProxy(AG)
        APT = AP[int]

        ap = AP()
        apt = APT()

        self.assertTrue(hasattr(ap, '__enforcer__'))
        self.assertTrue(hasattr(apt, '__enforcer__'))

        # Signature in generics should always point to the original unconstrained generic
        self.assertEqual(ap.__enforcer__.signature, AP.__wrapped__)
        self.assertEqual(apt.__enforcer__.signature, AP.__wrapped__)

        self.assertEqual(ap.__enforcer__.generic, AP.__enforcer__.generic)
        self.assertEqual(apt.__enforcer__.generic, APT.__enforcer__.generic)

        self.assertEqual(ap.__enforcer__.bound, AP.__enforcer__.bound)
        self.assertEqual(apt.__enforcer__.bound, APT.__enforcer__.bound)

        for hint_name, hint_value in apt.__enforcer__.hints.items():
            self.assertEqual(hint_value, APT.__enforcer__.hints[hint_name])

        self.assertEqual(len(apt.__enforcer__.hints), len(APT.__enforcer__.hints))

    def test_generic_constraints_are_validated(self):
        """
        Verifies that proxied generic constraints cannot contradict the TypeVar definition
        """
        T = TypeVar('T', int, str)

        class AG(Generic[T]):
            pass

        AP = GenericProxy(AG)
        APT = AP[int]
        APT = AP[str]

        with self.assertRaises(TypeError):
            APT = AP[tuple]


if __name__ == '__main__':
    unittest.main()
