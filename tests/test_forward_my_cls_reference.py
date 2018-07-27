import unittest

from enforce.exceptions import RuntimeTypeError

from enforce import runtime_validation


class TestForwardMyClsReference(unittest.TestCase):

    def test_it(self):
        class A:

            @runtime_validation
            def clone(self) -> 'A':
                return A()

        val = A().clone()
        self.assertIsInstance(val, A)

    def test_the_validation(self):
        try:
            class A:

                @runtime_validation
                def clone(self) -> 'A':
                    return 'str'

            A().clone()
        except RuntimeTypeError:
            pass
        else:
            raise Exception('A typerror should have been raised')
