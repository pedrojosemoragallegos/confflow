from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from confflow.types import Value

T = TypeVar("T", bound=Value)


class Constraint(ABC, Generic[T]):
    @abstractmethod
    def __call__(self, value: T) -> None: ...
