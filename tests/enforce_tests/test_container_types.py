import typing

import pytest

from enforce import runtime_validation
from enforce.exceptions import RuntimeTypeError


class TestContainerTypes:
    """
    Tests for the container types - including types of unbounded size
    """

    def test_forward_reference_container(self):
        @runtime_validation
        def foo(data: typing.Optional["A"]):
            return data.bar(10)

        @runtime_validation
        def bar(data: "B"):
            return data

        class A:
            def __init__(self, value: int):
                self.value = value

            def bar(self, value: int):
                return self.value * 2 + value

        class B:
            pass

        a = A(12)

        assert foo(a) == 34
        assert isinstance(bar(B()), B)

        with pytest.raises(RuntimeTypeError):
            foo(12)

        with pytest.raises(RuntimeTypeError):
            bar("B")
