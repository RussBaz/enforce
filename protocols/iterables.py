import types
import typing

from .general import Container, Sized

T = typing.TypeVar("T")


class Iterator(typing.Generic[T]):
    def __iter__(self) -> "Iterator[T]":
        pass

    def __next__(self) -> T:
        pass


class Iterable(typing.Generic[T]):
    def __iter__(self) -> Iterator[T]:
        pass


class Collection(Container, Sized, Iterable[T]):
    pass


class Reversible(Iterable[T]):
    def __reversed__(self) -> Iterator[T]:
        pass


class Generator(Iterable[T]):
    def send(self, value: typing.Optional):
        pass

    def throw(
        self,
        typ: BaseException,
        val: typing.Optional[typing.Type[BaseException]] = None,
        tb: typing.Optional[types.TracebackType] = None,
    ) -> None:
        pass

    def close(self) -> None:
        pass
