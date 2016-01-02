import unittest

from enforce import runtime_validation
from enforce.wrappers import Proxy


class WrappersTest(unittest.TestCase):

    def test_proxy_transparency(self):
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

    @unittest.skip
    def test_can_decorate(self):
        class A:
            def sample(self):
                return data

        a = A()
        proxy_a = Proxy(a)
        proxy_a.sample = runtime_validation(a.sample, a)

        self.assertEqual(proxy_a.sample(1), 1)


if __name__ == '__main__':
    unittest.main()
