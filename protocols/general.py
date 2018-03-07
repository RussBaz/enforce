import typing
import inspect

import enforce.domain_types as dt


T = typing.TypeVar('T')


class Container(typing.Generic[T]):
    def __contains__(self, item: T) -> bool: pass


class Hashable:
    def __hash__(self) -> int: pass


class Sized:
    def __len__(self) -> int: pass


class Callable:
    def __protocol_extra_check__(self, data: typing.Any) -> dt.ValidationResult:
        is_callable = (
            inspect.isfunction(data) or
            inspect.ismethod(data) or
            inspect.isclass(data)
            )

        if not is_callable:
            try:
                call = data.__call__
                is_callable = inspect.isfunction(call) or inspect.ismethod(call)
            except AttributeError:
                pass

        return dt.ValidationResult(valid=is_callable, data=data, type_name=type(data))
