from typing import Protocol, TypeVar, runtime_checkable


@runtime_checkable
class HasLen(Protocol):
    def __len__(self) -> int: ...


T = TypeVar("T", contravariant=True)


@runtime_checkable
class Constraint(Protocol[T]):
    def __call__(self, value: T) -> None: ...
