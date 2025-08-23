from typing import TypeVar, Union

from .constraint import Constraint

T = TypeVar("T", bound=Union[int, float])


class GreaterThan(Constraint[T]):
    def __init__(self, threshold: T):
        super().__init__(f"Value must be greater than {threshold}")
        self._threshold = threshold

    def validate(self, value: T) -> bool:
        return value > self._threshold


class GreaterThanOrEqual(Constraint[T]):
    def __init__(self, threshold: T):
        super().__init__(f"Value must be >= {threshold}")
        self._threshold = threshold

    def validate(self, value: T) -> bool:
        return value >= self._threshold


class LessThan(Constraint[T]):
    def __init__(self, threshold: T):
        super().__init__(f"Value must be less than {threshold}")
        self._threshold = threshold

    def validate(self, value: T) -> bool:
        return value < self._threshold


class LessThanOrEqual(Constraint[T]):
    def __init__(self, threshold: T):
        super().__init__(f"Value must be <= {threshold}")
        self._threshold = threshold

    def validate(self, value: T) -> bool:
        return value <= self._threshold
