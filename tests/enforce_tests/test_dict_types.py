import typing
import unittest

from enforce import runtime_validation, config
from enforce.exceptions import RuntimeTypeError


class DictTypesTests(unittest.TestCase):
    """
    Tests for the dictionary types
    """

    def test_simple_dict(self):
        """
        Verifies that unrestricted Dictionary type is correctly checked
        """
        d = {'a': 12, 'b': 'b'}

        @runtime_validation
        def foo(a: typing.Dict, b: typing.Any=None) -> typing.Dict:
            return b

        foo(d, d)

        with self.assertRaises(RuntimeTypeError):
            foo(3)

        with self.assertRaises(RuntimeTypeError):
            foo(d, 2)

    def test_empty_dict(self):
        """
        Verifies that empty dictionary is treated correctly
        """
        @runtime_validation
        def foo(a: typing.Any) -> typing.Dict:
            return dict()

        foo(12)

    def test_dict_is_mapping(self):
        """
        Verifies that dictionary is treated like a Mapping
        """
        config({'mode': 'covariant'})

        @runtime_validation
        def returns_dict() -> typing.Mapping:
            return dict()

        returns_dict()

        config(reset=True)

    def test_restricted_dict(self):
        """
        Verifies that restricted dictionaries are type checked correctly
        """
        TypeAlias = typing.Dict[str, typing.Union[int, str, None]]

        @runtime_validation
        def foo(a: TypeAlias, b: typing.Any=None) -> TypeAlias:
            return b

        good_dict = {
            'hello': 'world',
            'name': None,
            'id': 1234
        }

        bad_dict = {
            'hello': 123.5
        }

        foo(good_dict, good_dict)

        with self.assertRaises(RuntimeTypeError):
            foo(bad_dict)

        with self.assertRaises(RuntimeTypeError):
            foo(good_dict, bad_dict)

        foo({}, {})

    def test_nested_dicts(self):
        """
        Verifies that the type containing nested dictionaries can be successfully verified
        """
        TypeAlias = typing.Dict[str, typing.Dict[str, typing.Optional[int]]]

        @runtime_validation
        def foo(a: TypeAlias, b: typing.Any=None) -> TypeAlias:
            return b

        good_dict = {
            'hello': {
                'world': 12,
                'me': None
            }
        }

        bad_dict = {
            12: None
        }

        bad_dict_2 = {
            'hello': {
                'world': 12,
                'everyone': None,
                'me': {1, 3},
                2: {'a': 'a'}
            }
        }

        foo(good_dict, good_dict)

        with self.assertRaises(RuntimeTypeError):
            foo(bad_dict)

        with self.assertRaises(RuntimeTypeError):
            foo(good_dict, bad_dict)

        with self.assertRaises(RuntimeTypeError):
            foo(bad_dict_2)

        with self.assertRaises(RuntimeTypeError):
            foo(good_dict, bad_dict_2)