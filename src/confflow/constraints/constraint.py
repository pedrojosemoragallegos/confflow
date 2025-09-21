from __future__ import annotations

import typing
from abc import ABC, abstractmethod

T = typing.TypeVar("T")


class Constraint(ABC, typing.Generic[T]):
    def __init__(self, description: str) -> None:
        self._description: str = description

    def __call__(self, value: T) -> None:
        if not self.validate(value):
            raise ValueError(f"{self._description}, got: {value}")  # noqa: EM102, TRY003

    @abstractmethod
    def validate(self, value: T) -> bool: ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._description!r})"
