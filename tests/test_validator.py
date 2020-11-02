import unittest

from enforce.exceptions import RuntimeTypeError


class ValidatorTests(unittest.TestCase):
    def test_literal(self):
        from typing import Literal
        from dataclasses import dataclass

        from enforce import runtime_validation

        @runtime_validation
        @dataclass
        class A(object):
            optimizer: Literal[
                "Adadelta", "Adagrad", "Adam", "Adamax", "Ftrl", "Nadam", "RMSprop"
            ] = None

        with self.assertRaises(RuntimeTypeError) as cm:
            A(optimizer="AdamX")

        self.assertEqual(len(cm.exception.args), 1)
        self.assertEqual(
            cm.exception.args[0].strip(),
            "The following runtime type errors were encountered:\n       "
            "Argument 'optimizer' was not of type "
            "typing.Literal['Adadelta', 'Adagrad', 'Adam', 'Adamax', 'Ftrl', 'Nadam', 'RMSprop']. "
            "Actual type was str.",
        )

        self.assertEqual(A(optimizer="Adam").optimizer, "Adam")


if __name__ == "__main__":
    unittest.main()
