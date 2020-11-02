import inspect
import typing
import unittest

from enforce.wrappers import EnforceProxy  # , ListProxy


class WrapperTests(unittest.TestCase):
    def test_proxy_transparency(self):
        """
        Verifies if the proxy transparency can be switched on and off at runtime
        If transparency is off, then if an attribute is changed, it is saved locally only
        In such case a copy with '_self_' prefix is created on a proxy itself.
        """

        class A(object):
            pass

        a = A()
        a.b = 1

        proxy_a = EnforceProxy(a, 12)
        proxy_a.b = 2

        B = EnforceProxy(A)
        b = B()

        def foo():
            return None

        C = EnforceProxy(A, foo)
        c = C()

        self.assertTrue(a.b, proxy_a.b)
        self.assertFalse(hasattr(a, "__enforcer__"))
        self.assertEqual(proxy_a.__enforcer__, 12)

        self.assertFalse(hasattr(A, "__enforcer__"))
        self.assertIsNone(B.__enforcer__)
        self.assertIsNone(b.__enforcer__)

        self.assertIs(C.__enforcer__, foo)
        self.assertIs(c.__enforcer__, foo)

    # def test_list_proxy(self):
    #    a = [1, 2]
    #    b = ListProxy(a)
    #    b.append(3)
    #    a.reverse()

    #    self.assertEqual(a, b)
    #    self.assertFalse(a is b)
    #    self.assertTrue(a is b.__wrapped__)
    #    self.assertTrue(isinstance(b, list))
    #    self.assertTrue(isinstance(b, ObjectProxy))

    def test_enforceable_proxy(self):
        def foo(input: typing.Any) -> typing.Any:
            pass

        foo_proxy = EnforceProxy(foo)

        self.assertTrue(hasattr(foo_proxy, "__enforcer__"))
        self.assertFalse(hasattr(foo, "__enforcer__"))
        self.assertIs(foo, foo_proxy.__wrapped__)
        self.assertIsNone(foo_proxy.__enforcer__)

        tmp_number = 1
        foo_proxy.__enforcer__ = tmp_number

        self.assertEqual(foo_proxy.__enforcer__, tmp_number)
        self.assertFalse(hasattr(foo, "__enforcer__"))

        inspect.signature(foo_proxy)


if __name__ == "__main__":
    unittest.main()
