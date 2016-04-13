import unittest

from wrapt import ObjectProxy

from enforce import runtime_validation
from enforce.wrappers import Proxy, ListProxy


class WrappersTest(unittest.TestCase):

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

    def test_new(self):
        a = [1, 2]
        b = ListProxy(None, None, a)
        b.append(3)
        a.reverse()

        self.assertEqual(a, b)
        self.assertFalse(a is b)
        self.assertTrue(isinstance(b, list))
        self.assertTrue(isinstance(b, ObjectProxy))


if __name__ == '__main__':
    unittest.main()
