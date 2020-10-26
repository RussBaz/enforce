from __future__ import absolute_import

import sys
import unittest

import pytest

from enforce.protocol import register, is_registered, deregister_all


class TestProtocol(unittest.TestCase):
    def setUp(self):
        deregister_all(do_it=True)

    def test_register_deregister(self):
        class A:
            __protocol_name__ = "main.A"

        protocol_definition = register(A)
        self.assertTrue(is_registered(A))
        deregister_all()
        self.assertTrue(is_registered(A))
        deregister_all(do_it=True)
        self.assertFalse(is_registered(A))
        self.assertEqual(protocol_definition.id, A.__protocol_name__)

    def test_simple_protocol_registration(self):
        class A:
            def foo(self):
                pass

            def foo_1(self, data: int):
                pass

            def foo_2(self, data: str) -> int:
                pass

            __protocol_name__ = "main.A"

        self.assertFalse(is_registered(A.__protocol_name__))

        protocol_definition = register(A)

        self.assertTrue(is_registered(A.__protocol_name__))

        p_id, fields, extra_tests = protocol_definition

        expected_result = {
            "__class__": "(Assertion) Field Guard for: typing.Callable",
            "__delattr__": "(Assertion) Field Guard for: typing.Callable",
            "__dir__": "(Assertion) Field Guard for: typing.Callable",
            "__doc__": "(Assertion) Field Guard for: typing.Any",
            "__eq__": "(Assertion) Field Guard for: typing.Callable",
            "__format__": "(Assertion) Field Guard for: typing.Callable",
            "__ge__": "(Assertion) Field Guard for: typing.Callable",
            "__getattribute__": "(Assertion) Field Guard for: typing.Callable",
            "__gt__": "(Assertion) Field Guard for: typing.Callable",
            "__hash__": "(Assertion) Field Guard for: typing.Callable",
            "__init__": "(Assertion) Field Guard for: typing.Callable",
            "__init_subclass__": "(Assertion) Field Guard for: typing.Callable",
            "__le__": "(Assertion) Field Guard for: typing.Callable",
            "__lt__": "(Assertion) Field Guard for: typing.Callable",
            "__ne__": "(Assertion) Field Guard for: typing.Callable",
            "__new__": "(Assertion) Field Guard for: typing.Callable",
            "__reduce__": "(Assertion) Field Guard for: typing.Callable",
            "__reduce_ex__": "(Assertion) Field Guard for: typing.Callable",
            "__repr__": "(Assertion) Field Guard for: typing.Callable",
            "__setattr__": "(Assertion) Field Guard for: typing.Callable",
            "__sizeof__": "(Assertion) Field Guard for: typing.Callable",
            "__str__": "(Assertion) Field Guard for: typing.Callable",
            "__subclasshook__": "(Assertion) Field Guard for: typing.Callable",
            "foo": "(Assertion) Field Guard for: typing.Callable",
            "foo_1": "(Assertion) Field Guard for: typing.Callable[[int], typing.Any]",
            "foo_2": "(Assertion) Field Guard for: typing.Callable[[str], int]",
        }

        self.assertEqual(p_id, A.__protocol_name__)
        self.assertEqual(len(fields), len(expected_result))

        for k, v in expected_result.items():
            with self.subTest(k=k):
                self.assertEqual(str(fields[k]), v)

        self.assertIsNone(extra_tests)

    @pytest.mark.skipif(
        sys.version_info < (3, 8), reason="Test for Python 3.6.x+ syntax only"
    )
    def test_parent(self):
        if sys.version_info < (3, 8):
            return
        from .protocol_test import _test_parent
        _test_parent(self)
