import unittest
import typing
from typing import Any, Optional

import enforce
from enforce.exceptions import RuntimeTypeError


class DecoratorsTests(unittest.TestCase):
    """
    A container for decorator related tests
    """

    def test_validation(self):
        """
        Verifies that a valid input and output result in no exception raised,
        invalid input results in a RuntimeTypeError exception being raised,
        invalid output results in a RuntimeTypeError exception being raised. 
        """
        @enforce.runtime_validation
        def test(text: str) -> None:
            output = text * 2
            return None

        @enforce.runtime_validation
        def test2(text: str) -> None:
            return text

        message = 'hello world' # Assumed to be string
        invalid_argument = 12   # Assumed to be integer

        error_code_1 = "Argument 'text' ('{0}') was not of type <class 'str'>. Actual type was <class 'int'>.".format(invalid_argument)
        error_code_2 = "Return value '{0}' was not of type <class 'NoneType'>. Actual type was <class 'str'>.".format(message)

        self.assertIsNone(test(message))

        with self.assertRaises(RuntimeTypeError) as cm_1:
            test(invalid_argument)

        self.assertEqual(error_code_1, cm_1.exception.__str__())

        with self.assertRaises(RuntimeTypeError) as cm_2:
            test2(message)

        self.assertEqual(error_code_2, cm_2.exception.__str__())

    def test_any_and_partial_validation(self):
        """
        Verifies that validation still works if only some inputs have type hints
        """
        @enforce.runtime_validation
        def test(param, text: str, val:Any, last:Optional[int]=None) -> str:
            output = text * 2
            return text

        @enforce.runtime_validation
        def test2(param, text: str, val:Any, last:Optional[int]=None) -> str:
            output = text * 2
            return None

        param_1 = '12'
        text_1 = 'hello'
        val_1 = {'integer': 12}
        last_1 = 1

        self.assertEqual(test(param_1, text_1, val_1, last_1), text_1)

        param_2 = test
        text_2 = 'hello'
        val_2 = object()
        last_2 = None

        self.assertEqual(test(param_2, text_2, val_2, last_2), text_2)
        self.assertEqual(test(param_2, text_2, val_2), text_2)

        param_3 = '12'
        text_3 = 12
        val_3 = None
        last_3 = -999

        error_message_3 = "Argument 'text' ('{0}') was not of type <class 'str'>. Actual type was {1}.".format(text_3, type(text_3))

        with self.assertRaises(RuntimeTypeError) as cm:
            test(param_3, text_3, val_3, last_3)

        self.assertEqual(error_message_3, cm.exception.__str__())

        param_4 = '12'
        text_4 = 'hello'
        val_4 = {'integer': 12}
        last_4 = 1

        error_message_4 = "Return value '{0}' was not of type <class 'str'>. Actual type was {1}.".format(None, type(None))

        with self.assertRaises(RuntimeTypeError) as cm:
            test2(param_4, text_4, val_4, last_4)

        self.assertEqual(error_message_4, cm.exception.__str__())

    def test_all_exceptions_returned(self):
        """
        Verifies that if more than one input parameter is not validated,
        then a single exception raised with an error message with all invalidated parameters
        """
        @enforce.runtime_validation
        def test(param, text: str, val:Any, last:Optional[int]=None) -> str:
            output = text * 2
            return text

        param = '12'
        text = 12
        val = {'integer': 12}
        last = 'hello'

        error_message_last = "Argument 'last' ('{0}') was not of type typing.Union[int, NoneType]. Actual type was {1}".format(last, type(last))
        error_message_text = "Argument 'text' ('{0}') was not of type <class 'str'>. Actual type was {1}.".format(text, type(text))

        with self.assertRaises(RuntimeTypeError) as cm:
            test(param, text, val, last)

        error_message = cm.exception.__str__()

        self.assertIn(error_message_last, error_message)
        self.assertIn(error_message_text, error_message)

    def test_docstring_and_name_presrved(self):
        """
        Verifies that an original name and a docstring are preserved
        """
        def test(text: str) -> None:
            """I am a docstring"""
            print(text)

        original_name = test.__name__
        original_doc = test.__doc__

        @enforce.runtime_validation
        def test(text: str) -> None:
            """I am a docstring"""
            print(text)

        self.assertEqual(original_doc, test.__doc__)
        self.assertEqual(original_name, test.__name__)

    def test_working_callable_argument(self):
        @enforce.runtime_validation
        def foo(func: typing.Callable[[int], str], bar: int) -> str:
            return func(bar)

        try:
            foo(lambda x: str(x), 5)
        except enforce.exceptions.RuntimeTypeError:
            print('Callable Argument Raised Error!')
            raise

    def test_tuple_support(self):
        @enforce.runtime_validation
        def test(tup: typing.Tuple[int, str, float]) -> typing.Tuple[str, int]:
            return tup[1], tup[0]

        tup = ('a', 5, 3.0)
        try:
            test(tup)
            raise AssertionError
        except enforce.exceptions.RuntimeTypeError:
            pass



if __name__ == '__main__':
    unittest.main()
