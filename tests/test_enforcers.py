import unittest
from typing import Any, Callable, TypeVar, Generic, no_type_check

from enforce.enforcers import get_enforcer, Enforcer, GenericProxy
from enforce.settings import Settings


class EnforcerTests(unittest.TestCase):
    def func_int___none(self):
        def func_int___none(a: int) -> None:
            pass

        return func_int___none

    def func_int_empty___none(self):
        def func_int_empty___none(a: int, b) -> None:
            pass

        return func_int_empty___none

    def func_int_empty___empty(self):
        def func_int_empty___empty(a: int, b):
            pass

        return func_int_empty___empty

    def func_empty_int_empty___empty(self):
        def func_empty_int_empty___empty(a, b: int, c):
            pass

        return func_empty_int_empty___empty

    def func_args_kwargs__empty(self):
        def func_args_kwargs__empty(*args, **kwargs):
            pass

        return func_args_kwargs__empty

    def func_args_kwargs__none(self):
        def func_args_kwargs__none(*args, **kwargs) -> None:
            pass

        return func_args_kwargs__none

    def func_args__empty(self):
        def func_args__empty(*args):
            pass

        return func_args__empty

    def func_empty_args__empty(self):
        def func_empty_args__empty(a, *args):
            pass

        return func_empty_args__empty

    def func_any_args__none(self):
        def func_any_args__none(a: Any, *args) -> None:
            pass

        return func_any_args__none

    def test_can_get_enforcer(self):
        self.assertIsInstance(get_enforcer(self.func_int___none()), Enforcer)

    def test_callable_simple_type(self):
        func_type = self.get_function_type(self.func_int___none())

        self.assertEqual(func_type, Callable[[int], None])

    def test_callable_without_known_return_is_any(self):
        func_type = self.get_function_type(self.func_int_empty___empty())
        args = func_type.__args__
        self.assertEqual(len(args), 3)
        self.assertEqual(args[0], int)
        self.assertEqual(args[1], Any)
        self.assertEqual(args[2], Any)

    def test_callable_missing_annotation(self):
        func_type = self.get_function_type(self.func_int_empty___none())

        self.assertEqual(func_type, Callable[[int, Any], None])

        func_type = self.get_function_type(self.func_int_empty___empty())

        self.assertEqual(func_type, Callable[[int, Any], Any])

        func_type = self.get_function_type(self.func_empty_int_empty___empty())

        self.assertEqual(func_type, Callable[[Any, int, Any], Any])

    def test_with_kwargs(self):
        func_type = self.get_function_type(self.func_args_kwargs__empty())

        self.assertEqual(func_type, Callable)

    def test_with_kwargs_and_return(self):
        func_type = self.get_function_type(self.func_args_kwargs__none())
        print(func_type)
        self.assertEqual(func_type, Callable[..., None])

    def test_any_positional_only(self):
        func_type = self.get_function_type(self.func_args__empty())

        self.assertEqual(func_type, Callable)

    def test_any_extra_positional_only(self):
        func_type = self.get_function_type(self.func_empty_args__empty())

        self.assertEqual(func_type, Callable[[Any], Any])

    def test_any_positional_with_return(self):
        func_type = self.get_function_type(self.func_any_args__none())

        self.assertEqual(func_type, Callable[[Any], None])

    def test_deactivated_callable(self):
        """
        Disabled enforcers should be returning just Callable
        """
        settings = Settings(enabled=False)

        func = no_type_check(self.func_int___none())
        func_type = self.get_function_type(func)

        self.assertIs(func_type, Callable)

        func = self.func_int___none()

        self.assertFalse(hasattr(func, "__enforcer__"))

        enforcer = get_enforcer(func, settings=settings)
        func_type = enforcer.callable_signature

        self.assertIsNotNone(enforcer.settings)
        self.assertFalse(enforcer.settings)
        self.assertFalse(enforcer.settings.enabled)
        self.assertEqual(func_type, Callable)

    @staticmethod
    def get_function_type(func):
        return get_enforcer(func).callable_signature


class GenericProxyTests(unittest.TestCase):
    def test_can_proxy_generic(self):
        """
        Verifies that Generic Proxy wraps the original user defined generic
        and applies an enforcer to it
        """
        T = TypeVar("T")
        K = TypeVar("K")
        V = TypeVar("V")

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

        self.assertFalse(hasattr(AG, "__enforcer__"))
        self.assertFalse(hasattr(BG, "__enforcer__"))

    def test_applying_to_another_proxy(self):
        """
        Verifies that applying Generic Proxy to another Generic Proxy
        will result in a new generic proxy of wrapped object being returned
        """
        T = TypeVar("T")

        class AG(Generic[T]):
            pass

        AGTA = GenericProxy(AG)
        AGTB = GenericProxy(AGTA)

        self.assertIsNot(AGTA, AGTB)
        self.assertIs(AGTA.__wrapped__, AG)
        self.assertIs(AGTB.__wrapped__, AG)

        self.assertIs(AGTA.__enforcer__.signature, AG)
        self.assertIs(AGTB.__enforcer__.signature, AG)

    def test_typed_generic_is_proxied(self):
        """
        Verifies that when Generic Proxy is constrained, the returned generic is also wrapped in a Generic Proxy
        And its origin property is pointing to a parent Generic Proxy (not an original user defined generic)
        """
        types = (int, int, str)

        T = TypeVar("T")
        K = TypeVar("K")
        V = TypeVar("V")

        T_t, K_t, V_t = types

        class AG(Generic[T, K, V]):
            pass

        AP = GenericProxy(AG)

        AGT = AG[T_t, K_t, V_t]
        APT = AP[T_t, K_t, V_t]

        self.assertFalse(hasattr(AGT, "__enforcer__"))

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
        T = TypeVar("T")

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
        T = TypeVar("T")

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
        In addition, this __enforcer__ object must have settings and by default type validation should be enabled
        """
        T = TypeVar("T")

        class AG(Generic[T]):
            pass

        AP = GenericProxy(AG)
        APT = AP[int]

        ap = AP()
        apt = APT()

        self.assertTrue(hasattr(ap, "__enforcer__"))
        self.assertTrue(hasattr(apt, "__enforcer__"))

        # Signature in generics should always point to the original unconstrained generic
        self.assertEqual(ap.__enforcer__.signature, AG)
        self.assertEqual(apt.__enforcer__.signature, AG)

        self.assertEqual(ap.__enforcer__.generic, AP.__enforcer__.generic)
        self.assertEqual(apt.__enforcer__.generic, APT.__enforcer__.generic)

        self.assertEqual(ap.__enforcer__.bound, AP.__enforcer__.bound)
        self.assertEqual(apt.__enforcer__.bound, APT.__enforcer__.bound)

        for hint_name, hint_value in apt.__enforcer__.hints.items():
            self.assertEqual(hint_value, APT.__enforcer__.hints[hint_name])

        self.assertEqual(len(apt.__enforcer__.hints), len(APT.__enforcer__.hints))

        self.assertTrue(AP.__enforcer__.settings)
        self.assertTrue(APT.__enforcer__.settings)
        self.assertTrue(ap.__enforcer__.settings)
        self.assertTrue(apt.__enforcer__.settings)

    def test_generic_constraints_are_validated(self):
        """
        Verifies that proxied generic constraints cannot contradict the TypeVar definition
        """
        T = TypeVar("T", int, str)

        class AG(Generic[T]):
            pass

        AP = GenericProxy(AG)
        APT = AP[int]
        APT = AP[str]

        with self.assertRaises(TypeError):
            APT = AP[tuple]


if __name__ == "__main__":
    unittest.main()
