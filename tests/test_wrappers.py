import unittest
import typing
import inspect

from wrapt import ObjectProxy

from enforce import runtime_validation
from enforce.wrappers import Proxy, ListProxy, EnforceProxy


class WrapperTests(unittest.TestCase):

    def test_proxy_transparency(self):
        """
        Verifies if the proxy transparency can be switched on and off at runtime
        If transparency is off, then if an attribute is changed, it is saved locally only
        In such case a copy with '_self_' prefix is created on a proxy itself.
        """
        class A:
            pass

        a = A()
        a.b = 1

        proxy_a = Proxy(a)

        proxy_a.pass_through = False
        
        proxy_a.b = 2

        self.assertEqual(a.b, 1)
        self.assertEqual(proxy_a.b, 2)
        self.assertEqual(proxy_a._self_b, 2)

        proxy_a.pass_through = True

        self.assertEqual(a.b, 1)
        self.assertEqual(proxy_a.b, 1)
        self.assertEqual(proxy_a._self_b, 2)

        proxy_a.b = 3

        self.assertEqual(a.b, 3)
        self.assertEqual(proxy_a.b, 3)
        self.assertEqual(proxy_a._self_b, 2)

    def test_list_proxy(self):
        a = [1, 2]
        b = ListProxy(a)
        b.append(3)
        a.reverse()

        self.assertEqual(a, b)
        self.assertFalse(a is b)
        self.assertTrue(a is b.__wrapped__)
        self.assertTrue(isinstance(b, list))
        self.assertTrue(isinstance(b, ObjectProxy))

    def test_enforceable_proxy(self):
        def foo(input: typing.Any) -> typing.Any:
            pass

        foo_proxy = EnforceProxy(foo)

        self.assertTrue(hasattr(foo_proxy, '__enforcer__'))
        self.assertFalse(hasattr(foo, '__enforcer__'))
        self.assertIs(foo, foo_proxy.__wrapped__)
        self.assertIsNone(foo_proxy.__enforcer__)

        temp_number = 1
        foo_proxy.__enforcer__ = temp_number

        self.assertEqual(foo_proxy.__enforcer__, temp_number)
        self.assertFalse(hasattr(foo, '__enforcer__'))

        inspect.signature(foo_proxy)


if __name__ == '__main__':
    unittest.main()
