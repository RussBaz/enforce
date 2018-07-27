import unittest

from enforce.exceptions import RuntimeTypeError

from enforce import runtime_validation


class TestForwardMyClsReference(unittest.TestCase):

    def test_output_ok(self):
        class A:

            @runtime_validation
            def clone(self) -> 'A':
                return A()

        val = A().clone()
        self.assertIsInstance(val, A)

    def test_output_fail(self):
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

    def test_input_ok(self):
        class A:

            @runtime_validation
            def __eq__(self, other: 'A') -> bool:
                return self is other

        a = A()
        assert a == a

    def test_input_not_ok(self):
        class A:

            @runtime_validation
            def __eq__(self, other: 'A') -> bool:
                return self is other

        a = A()
        try:
            a == 'a'
        except RuntimeTypeError:
            pass
        else:
            raise Exception('A typerror should have been raised')

    def test_input_fwd_ref_other_type(self):
        class B:
            pass

        class A:

            @runtime_validation
            def __eq__(self, other: 'B') -> bool:
                return self is other

        a = A()
        b = B()
        assert a != b
