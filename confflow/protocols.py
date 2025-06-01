from typing import Protocol, runtime_checkable


@runtime_checkable
class Sizeable(Protocol):
    def __len__(self) -> int: ...
