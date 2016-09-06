import unittest

from enforce.exceptions import RuntimeTypeError


class ExceptionsTests(unittest.TestCase):
    """
    A container for custom exceptions related tests
    """

    def test_raises_runtime_type_error(self):
        """
        Verifies that an exception can be raised and it returns a correct message
        """
        message = 'hello world'
        with self.assertRaises(RuntimeTypeError) as error:
            raise RuntimeTypeError(message)

        self.assertEqual(message, error.exception.__str__())

if __name__ == '__main__':
    unittest.main()
