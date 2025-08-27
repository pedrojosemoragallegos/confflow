from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from confflow.types import Value

T = TypeVar("T", bound=Value)


class Constraint(ABC, Generic[T]):
    def __init__(self, description: str):
        self._description: str = description

    def __call__(self, value: T):
        if not self.validate(value):
            raise ValueError(f"{self._description}, got: {value}")

    @abstractmethod
    def validate(self, value: T) -> bool: ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._description!r})"
