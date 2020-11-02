import unittest
from pprint import pprint
from typing import Optional, Union, Dict, List, Tuple

from enforce.assertions import get_assert_for
from enforce.exceptions import RuntimeTypeError


class AssertionsTests(unittest.TestCase):
    def test_basic_assertion_generation(self):
        assert_int = get_assert_for(int)

        assert_int(12)

        with self.assertRaises(RuntimeTypeError):
            assert_int("hello world")

        assert_complex = get_assert_for(
            Union[Dict[str, Optional[Union[int, List[int]]]], List[Tuple[str, int]]]
        )
        data1 = [("a", 12), ("b", 123)]
        data2 = {"a": 12, "b": [12, 123, 3], "c": None}
        data3 = {"a": 12, "b": [12, 123, 3], "c": "d"}

        assert_complex(data1)
        assert_complex(data2)

        with self.assertRaises(RuntimeTypeError):
            assert_complex(data3)

    def test_returns_input(self):
        assert_str = get_assert_for(str)

        data = "hello string"

        self.assertEqual(assert_str(data), data)

        with self.assertRaises(RuntimeTypeError):
            assert_str(1)

    def test_string_representation(self):
        expected_message_template = "(Assertion) Field Guard for: {definition}"
        definition = Union[
            Dict[str, Optional[Union[int, List[int]]]], List[Tuple[str, int]]
        ]
        expected_message = expected_message_template.format(definition=definition)

        assert_complex = get_assert_for(definition)
        as_string = str(assert_complex)

        self.assertEqual(expected_message, as_string)
        pprint(as_string)


if __name__ == "__main__":
    unittest.main()
