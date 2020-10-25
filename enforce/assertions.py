import typing

from . import domain_types as dt


class Assertion(dt.FieldGuard[dt.T]):
    def __init__(self, assert_func) -> None:
        self.assert_func = assert_func

    def __call__(self, data: typing.Type[dt.T]) -> typing.Type[dt.T]:
        return self.assert_func(data)

    def __str__(self) -> str:
        message = "(Assertion) Field Guard for: {definition}"
        hint = self.assert_func.__enforcer__.hints.get("data")
        as_string = message.format(definition=hint)
        return as_string


def get_assert_for(definition: dt.T) -> Assertion[dt.T]:
    from .decorators import runtime_validation

    @runtime_validation
    def assert_of_type(data: definition):
        return data

    return Assertion[definition](assert_of_type)
