from typing import TypeAlias, TypeVar, Union

from .constraint import Constraint

T = TypeVar("T")
Number: TypeAlias = Union[int, float]


class NonNegative(Constraint[Number]):
    def __call__(self, value: Number) -> None:
        if value < 0:
            raise ValueError("Value must not be negative.")


class IsPositive(Constraint[Number]):
    def __call__(self, value: Number) -> None:
        if value <= 0:
            raise ValueError("Value must be positive (> 0).")


class IsNegative(Constraint[Number]):
    def __call__(self, value: Number) -> None:
        if value >= 0:
            raise ValueError("Value must be negative (< 0).")


class NonZero(Constraint[Number]):
    def __call__(self, value: Number) -> None:
        if value == 0:
            raise ValueError("Value must not be zero.")


class GreaterThan(Constraint[Number]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, value: Number) -> None:
        if value <= self._threshold:
            raise ValueError(f"Value must be greater than {self._threshold}.")


class GreaterThanOrEqual(Constraint[Number]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, value: Number) -> None:
        if value < self._threshold:
            raise ValueError(f"Value must be ≥ {self._threshold}.")


class LessThan(Constraint[Number]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, value: Number) -> None:
        if value >= self._threshold:
            raise ValueError(f"Value must be less than {self._threshold}.")


class LessThanOrEqual(Constraint[Number]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, value: Number) -> None:
        if value > self._threshold:
            raise ValueError(f"Value must be ≤ {self._threshold}.")


class BetweenInclusive(Constraint[Number]):
    def __init__(self, min_value: float, max_value: float) -> None:
        self._min_value = min_value
        self._max_value = max_value

    def __call__(self, value: Number) -> None:
        if not (self._min_value <= value <= self._max_value):
            raise ValueError(
                f"Value must be between {self._min_value} and {self._max_value} inclusive."
            )


class BetweenExclusive(Constraint[Number]):
    def __init__(self, min_value: float, max_value: float) -> None:
        self._min_value = min_value
        self._max_value = max_value

    def __call__(self, value: Number) -> None:
        if not (self._min_value < value < self._max_value):
            raise ValueError(
                f"Value must be strictly between {self._min_value} and {self._max_value}."
            )


## Integer Constraint
class IsEven(Constraint[int]):
    def __call__(self, value: int) -> None:
        if value % 2 != 0:
            raise ValueError("Value must be even.")


class IsOdd(Constraint[int]):
    def __call__(self, value: int) -> None:
        if value % 2 != 1:
            raise ValueError("Value must be odd.")


class MultipleOf(Constraint[int]):
    def __init__(self, base: int) -> None:
        if base == 0:
            raise ValueError("Base must not be zero.")
        self.base = base

    def __call__(self, value: int) -> None:
        if value % self.base != 0:
            raise ValueError(f"Value must be a multiple of {self.base}.")


class Divides(Constraint[int]):
    def __init__(self, divisor: int) -> None:
        if divisor == 0:
            raise ValueError("Divisor must not be zero.")
        self.divisor = divisor

    def __call__(self, value: int) -> None:
        if value == 0 or self.divisor % value != 0:
            raise ValueError(f"{value} does not divide {self.divisor}.")


class IsPrime(Constraint[int]):
    def __call__(self, value: int) -> None:
        value = value
        if value < 2:
            raise ValueError("Value must be a prime number.")
        for i in range(2, int(value**0.5) + 1):
            if value % i == 0:
                raise ValueError("Value is not a prime number.")


class IsPowerOfTwo(Constraint[int]):
    def __call__(self, value: int) -> None:
        value = value
        if value <= 0 or (value & (value - 1)) != 0:
            raise ValueError("Value must be a power of two.")


class IsNonNegativeInteger(Constraint[int]):
    def __call__(self, value: int) -> None:
        if value < 0:
            raise ValueError("Value must be a non-negative integer.")
