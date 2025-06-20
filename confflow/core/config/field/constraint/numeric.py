from typing import TypeAlias, TypeVar, Union

from .constraint import Constraint

T = TypeVar("T")

Number: TypeAlias = Union[int, float]


class GreaterThan(Constraint[int]):
    def __init__(self, threshold: int) -> None:
        super().__init__(f"Value must be greater than {threshold}")
        self._threshold = threshold

    def validate(self, value: int) -> bool:
        return value > self._threshold

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._threshold})"


class GreaterThanOrEqual(Constraint[int]):
    def __init__(self, threshold: int) -> None:
        super().__init__(f"Value must be >= {threshold}")
        self._threshold = threshold

    def validate(self, value: int) -> bool:
        return value >= self._threshold

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._threshold})"


class LessThan(Constraint[int]):
    def __init__(self, threshold: int) -> None:
        super().__init__(f"Value must be less than {threshold}")
        self._threshold = threshold

    def validate(self, value: int) -> bool:
        return value < self._threshold

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._threshold})"


class LessThanOrEqual(Constraint[int]):
    def __init__(self, threshold: int) -> None:
        super().__init__(f"Value must be <= {threshold}")
        self._threshold = threshold

    def validate(self, value: int) -> bool:
        return value <= self._threshold

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._threshold})"
