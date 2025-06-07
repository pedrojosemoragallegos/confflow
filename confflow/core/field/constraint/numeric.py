from typing import TypeVar

from confflow.core.types import (
    IntegerFieldValue,
    NumberFieldValue,
)

from .constraint import BaseConstraint

T = TypeVar("T")


class NonNegative(BaseConstraint[NumberFieldValue]):
    def __call__(self, value: NumberFieldValue) -> None:
        if value < 0:
            raise ValueError("Value must not be negative.")


class IsPositive(BaseConstraint[NumberFieldValue]):
    def __call__(self, value: NumberFieldValue) -> None:
        if value <= 0:
            raise ValueError("Value must be positive (> 0).")


class IsNegative(BaseConstraint[NumberFieldValue]):
    def __call__(self, value: NumberFieldValue) -> None:
        if value >= 0:
            raise ValueError("Value must be negative (< 0).")


class NonZero(BaseConstraint[NumberFieldValue]):
    def __call__(self, value: NumberFieldValue) -> None:
        if value == 0:
            raise ValueError("Value must not be zero.")


class GreaterThan(BaseConstraint[NumberFieldValue]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, value: NumberFieldValue) -> None:
        if value <= self._threshold:
            raise ValueError(f"Value must be greater than {self._threshold}.")


class GreaterThanOrEqual(BaseConstraint[NumberFieldValue]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, value: NumberFieldValue) -> None:
        if value < self._threshold:
            raise ValueError(f"Value must be ≥ {self._threshold}.")


class LessThan(BaseConstraint[NumberFieldValue]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, value: NumberFieldValue) -> None:
        if value >= self._threshold:
            raise ValueError(f"Value must be less than {self._threshold}.")


class LessThanOrEqual(BaseConstraint[NumberFieldValue]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, value: NumberFieldValue) -> None:
        if value > self._threshold:
            raise ValueError(f"Value must be ≤ {self._threshold}.")


class BetweenInclusive(BaseConstraint[NumberFieldValue]):
    def __init__(self, min_value: float, max_value: float) -> None:
        self._min_value = min_value
        self._max_value = max_value

    def __call__(self, value: NumberFieldValue) -> None:
        if not (self._min_value <= value <= self._max_value):
            raise ValueError(
                f"Value must be between {self._min_value} and {self._max_value} inclusive."
            )


class BetweenExclusive(BaseConstraint[NumberFieldValue]):
    def __init__(self, min_value: float, max_value: float) -> None:
        self._min_value = min_value
        self._max_value = max_value

    def __call__(self, value: NumberFieldValue) -> None:
        if not (self._min_value < value < self._max_value):
            raise ValueError(
                f"Value must be strictly between {self._min_value} and {self._max_value}."
            )


## Integer BaseConstraint
class IsEven(BaseConstraint[IntegerFieldValue]):
    def __call__(self, value: IntegerFieldValue) -> None:
        if value % 2 != 0:
            raise ValueError("Value must be even.")


class IsOdd(BaseConstraint[IntegerFieldValue]):
    def __call__(self, value: IntegerFieldValue) -> None:
        if value % 2 != 1:
            raise ValueError("Value must be odd.")


class MultipleOf(BaseConstraint[IntegerFieldValue]):
    def __init__(self, base: int) -> None:
        if base == 0:
            raise ValueError("Base must not be zero.")
        self.base = base

    def __call__(self, value: IntegerFieldValue) -> None:
        if value % self.base != 0:
            raise ValueError(f"Value must be a multiple of {self.base}.")


class Divides(BaseConstraint[IntegerFieldValue]):
    def __init__(self, divisor: int) -> None:
        if divisor == 0:
            raise ValueError("Divisor must not be zero.")
        self.divisor = divisor

    def __call__(self, value: IntegerFieldValue) -> None:
        if value == 0 or self.divisor % value != 0:
            raise ValueError(f"{value} does not divide {self.divisor}.")


class IsPrime(BaseConstraint[IntegerFieldValue]):
    def __call__(self, value: IntegerFieldValue) -> None:
        value = value
        if value < 2:
            raise ValueError("Value must be a prime number.")
        for i in range(2, int(value**0.5) + 1):
            if value % i == 0:
                raise ValueError("Value is not a prime number.")


class IsPowerOfTwo(BaseConstraint[IntegerFieldValue]):
    def __call__(self, value: IntegerFieldValue) -> None:
        value = value
        if value <= 0 or (value & (value - 1)) != 0:
            raise ValueError("Value must be a power of two.")


class IsNonNegativeInteger(BaseConstraint[IntegerFieldValue]):
    def __call__(self, value: IntegerFieldValue) -> None:
        if value < 0:
            raise ValueError("Value must be a non-negative integer.")
