import typing
import unittest

from enforce.exceptions import (
    RuntimeTypeError,
    parse_errors,
    raise_errors,
    process_errors,
)


class ExceptionsTests(unittest.TestCase):
    """
    A container for custom exceptions related tests
    """

    def test_raises_runtime_type_error(self):
        """
        Verifies that an exception can be raised and it returns a correct message
        """
        message = "hello world"
        with self.assertRaises(RuntimeTypeError) as error:
            raise RuntimeTypeError(message)

        self.assertEqual(message, error.exception.__str__())

    def test_raise_exceptions_raise_any(self):
        """
        Verifies that any exception can be raised with any message
        """
        message = "hello world"
        exception = Exception

        with self.assertRaises(exception) as error:
            raise_errors(exception, message)

        self.assertEqual(str(error.exception), message)

    def test_default_processor(self):
        """
        Verifies that the default error processor would call a passed parser function with given parameters
        and then will raise an error
        """
        e = "Hello "
        h = "world"
        r = "!"

        message = e + h + r

        def parser(errors, hints, is_return):
            return errors + hints + is_return

        with self.assertRaises(RuntimeTypeError) as error:
            process_errors(parser, RuntimeTypeError, e, h, r)

        self.assertEqual(str(error.exception), message)

        with self.assertRaises(TypeError) as error:
            process_errors(parser, TypeError, e, h, r)

        self.assertEqual(str(error.exception), message)

    def test_default_parser_input(self):
        """
        Verifies that the format of the default error parser when used on input, is correct
        """
        error_message = (
            "       Argument '{0}' was not of type {1}. Actual type was {2}."
        )
        return_error_message = (
            "        Return value was not of type {0}. Actual type was {1}."
        )
        output = "\n  The following runtime type errors were encountered:"

        hints = {
            "a": int,
            "b": typing.Dict[str, typing.Optional[int]],
            "return": typing.Optional[int],
        }

        # Multiple errors

        errors = [("a", "typing.Dict"), ("b", "typing.Callable")]

        expected_message = output
        expected_message += "\n" + error_message.format("a", hints["a"], errors[0][1])
        expected_message += "\n" + error_message.format("b", hints["b"], errors[1][1])

        message = parse_errors(errors, hints)

        self.assertEqual(message, expected_message)

        # Single error

        errors = [("a", "int")]

        expected_message = output
        expected_message += "\n" + error_message.format("a", hints["a"], errors[0][1])

        message = parse_errors(errors, hints)

        self.assertEqual(message, expected_message)

        # No hint available

        errors = [("c", "typing.Union[str, int]")]

        expected_message = output
        expected_message += "\n" + error_message.format("c", type(None), errors[0][1])

        message = parse_errors(errors, hints)

        self.assertEqual(message, expected_message)

    def test_default_parser_output(self):
        """
        Verifies that the format of the default error parser when used on output, is correct
        """
        error_message = (
            "       Argument '{0}' was not of type {1}. Actual type was {2}."
        )
        return_error_message = (
            "        Return value was not of type {0}. Actual type was {1}."
        )
        output = "\n  The following runtime type errors were encountered:"

        hints = {
            "a": int,
            "b": typing.Dict[str, typing.Optional[int]],
            "return": typing.Optional[int],
        }

        # Single error

        errors = [
            ("return", "typing.Dict"),
        ]

        expected_message = output
        expected_message += "\n" + return_error_message.format(
            hints["return"], errors[0][1]
        )

        message = parse_errors(errors, hints, True)

        self.assertEqual(message, expected_message)

        # No return hint specified

        errors = [
            ("return", "typing.Dict"),
        ]

        # Do not forget: the return hint is deleted at this stage
        del hints["return"]

        expected_message = output
        expected_message += "\n" + return_error_message.format(type(None), errors[0][1])

        message = parse_errors(errors, hints, True)

        self.assertEqual(message, expected_message)


if __name__ == "__main__":
    unittest.main()
