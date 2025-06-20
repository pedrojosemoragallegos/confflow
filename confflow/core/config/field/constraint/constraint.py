from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from confflow.types import Value

T = TypeVar("T", bound=Value)


class Constraint(ABC, Generic[T]):
    def __init__(self, error_message: str):
        self._error_message: str = error_message

    def __call__(self, value: T):
        if not self.validate(value):
            raise ValueError(self._error_message)

    @abstractmethod
    def validate(self, value: T) -> bool: ...

    @abstractmethod  # TODO find a better way to not repeat
    def __repr__(self) -> str: ...
