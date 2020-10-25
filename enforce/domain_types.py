import typing


T = typing.TypeVar("T")

ValidationResult = typing.NamedTuple(
    "ValidationResult", [("valid", bool), ("data", typing.Any), ("type_name", str)]
)


ProtocolId = typing.NewType("ProtocolId", str)
FieldName = typing.NewType("FieldName", str)
FieldDefinition = typing.NewType("FieldDefinition", type)

FieldCheckResult = typing.NamedTuple(
    "FieldCheckResult", [("valid", bool), ("errors", typing.List[typing.Any])]
)
Fields = typing.Dict[FieldName, FieldDefinition]


class FieldGuard(typing.Generic[T]):
    def __call__(self, data: typing.Type[T]) -> typing.Type[T]:
        pass


FieldGuards = typing.Dict[FieldName, FieldGuard]


ProtocolDefinition = typing.NamedTuple(
    "ProtocolDefinition",
    [
        ("id", ProtocolId),
        ("fields", FieldGuards),
        (
            "extra_tests",
            typing.Optional[typing.Callable[[typing.Any], ValidationResult]],
        ),
    ],
)

ProtocolRegistry = typing.NewType(
    "ProtocolRegistry", typing.Dict[ProtocolId, ProtocolDefinition]
)
