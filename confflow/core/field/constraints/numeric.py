from confflow.protocols import Constraint
from confflow.types import Numerical


class IsPositive(Constraint[Numerical]):
    def __call__(self, value: Numerical) -> None:
        if value <= 0:
            raise ValueError("Value must be positive (> 0)")


class IsNegative(Constraint[Numerical]):
    def __call__(self, value: Numerical) -> None:
        if value >= 0:
            raise ValueError("Value must be negative (< 0)")


class IsNonZero(Constraint[Numerical]):
    def __call__(self, value: Numerical) -> None:
        if value == 0:
            raise ValueError("Value must not be zero")


class GreaterThan(Constraint[Numerical]):
    def __init__(self, threshold: Numerical) -> None:
        self._threshold = threshold

    def __call__(self, value: Numerical) -> None:
        if value <= self._threshold:
            raise ValueError(f"Value must be greater than {self._threshold}")


class GreaterThanOrEqual(Constraint[Numerical]):
    def __init__(self, threshold: Numerical) -> None:
        self._threshold = threshold

    def __call__(self, value: Numerical) -> None:
        if value < self._threshold:
            raise ValueError(f"Value must be ≥ {self._threshold}")


class LessThan(Constraint[Numerical]):
    def __init__(self, threshold: Numerical) -> None:
        self._threshold = threshold

    def __call__(self, value: Numerical) -> None:
        if value >= self._threshold:
            raise ValueError(f"Value must be less than {self._threshold}")


class LessThanOrEqual(Constraint[Numerical]):
    def __init__(self, threshold: Numerical) -> None:
        self._threshold = threshold

    def __call__(self, value: Numerical) -> None:
        if value > self._threshold:
            raise ValueError(f"Value must be ≤ {self._threshold}")


class BetweenInclusive(Constraint[Numerical]):
    def __init__(self, min_value: Numerical, max_value: Numerical) -> None:
        self._min_value = min_value
        self._max_value = max_value

    def __call__(self, value: Numerical) -> None:
        if not (self._min_value <= value <= self._max_value):
            raise ValueError(
                f"Value must be between {self._min_value} and {self._max_value} inclusive"
            )


class BetweenExclusive(Constraint[Numerical]):
    def __init__(self, min_value: Numerical, max_value: Numerical) -> None:
        self._min_value = min_value
        self._max_value = max_value

    def __call__(self, value: Numerical) -> None:
        if not (self._min_value < value < self._max_value):
            raise ValueError(
                f"Value must be strictly between {self._min_value} and {self._max_value}"
            )
