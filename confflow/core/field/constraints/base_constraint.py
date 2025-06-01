from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Constraint(ABC, Generic[T]):
    @abstractmethod
    def validate(self, value: T) -> None: ...
