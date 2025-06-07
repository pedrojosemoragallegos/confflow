from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseConstraint(ABC, Generic[T]):
    @abstractmethod
    def __call__(self, value: T) -> None: ...
