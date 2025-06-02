import re
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union

from confflow.core.field_values import (
    FloatFieldValue,
    IntegerFieldValue,
    StringFieldValue,
)

T = TypeVar(
    "T",
)


## Base FieldConstraint
class FieldConstraint(ABC, Generic[T]):
    @abstractmethod
    def __call__(self, value: T) -> None: ...


## Numeric FieldConstraint
NumberField = Union[IntegerFieldValue, FloatFieldValue]


class NonNegative(FieldConstraint[NumberField]):
    def __call__(self, value: NumberField) -> None:
        if value < 0:
            raise ValueError("Value must not be negative.")


class IsPositive(FieldConstraint[NumberField]):
    def __call__(self, value: NumberField) -> None:
        if value <= 0:
            raise ValueError("Value must be positive (> 0).")


class IsNegative(FieldConstraint[NumberField]):
    def __call__(self, value: NumberField) -> None:
        if value >= 0:
            raise ValueError("Value must be negative (< 0).")


class NonZero(FieldConstraint[NumberField]):
    def __call__(self, value: NumberField) -> None:
        if value == 0:
            raise ValueError("Value must not be zero.")


class GreaterThan(FieldConstraint[NumberField]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, value: NumberField) -> None:
        if value <= self._threshold:
            raise ValueError(f"Value must be greater than {self._threshold}.")


class GreaterThanOrEqual(FieldConstraint[NumberField]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, value: NumberField) -> None:
        if value < self._threshold:
            raise ValueError(f"Value must be ≥ {self._threshold}.")


class LessThan(FieldConstraint[NumberField]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, value: NumberField) -> None:
        if value >= self._threshold:
            raise ValueError(f"Value must be less than {self._threshold}.")


class LessThanOrEqual(FieldConstraint[NumberField]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, value: NumberField) -> None:
        if value > self._threshold:
            raise ValueError(f"Value must be ≤ {self._threshold}.")


class BetweenInclusive(FieldConstraint[NumberField]):
    def __init__(self, min_value: float, max_value: float) -> None:
        self._min_value = min_value
        self._max_value = max_value

    def __call__(self, value: NumberField) -> None:
        if not (self._min_value <= value <= self._max_value):
            raise ValueError(
                f"Value must be between {self._min_value} and {self._max_value} inclusive."
            )


class BetweenExclusive(FieldConstraint[NumberField]):
    def __init__(self, min_value: float, max_value: float) -> None:
        self._min_value = min_value
        self._max_value = max_value

    def __call__(self, value: NumberField) -> None:
        if not (self._min_value < value < self._max_value):
            raise ValueError(
                f"Value must be strictly between {self._min_value} and {self._max_value}."
            )


## Integer FieldConstraint
class IsEven(FieldConstraint[IntegerFieldValue]):
    def __call__(self, value: IntegerFieldValue) -> None:
        if value % 2 != 0:
            raise ValueError("Value must be even.")


class IsOdd(FieldConstraint[IntegerFieldValue]):
    def __call__(self, value: IntegerFieldValue) -> None:
        if value % 2 != 1:
            raise ValueError("Value must be odd.")


class MultipleOf(FieldConstraint[IntegerFieldValue]):
    def __init__(self, base: int) -> None:
        if base == 0:
            raise ValueError("Base must not be zero.")
        self.base = base

    def __call__(self, value: IntegerFieldValue) -> None:
        if value % self.base != 0:
            raise ValueError(f"Value must be a multiple of {self.base}.")


class Divides(FieldConstraint[IntegerFieldValue]):
    def __init__(self, divisor: int) -> None:
        if divisor == 0:
            raise ValueError("Divisor must not be zero.")
        self.divisor = divisor

    def __call__(self, value: IntegerFieldValue) -> None:
        if value == 0 or self.divisor % value != 0:
            raise ValueError(f"{value} does not divide {self.divisor}.")


class IsPrime(FieldConstraint[IntegerFieldValue]):
    def __call__(self, value: IntegerFieldValue) -> None:
        value = value
        if value < 2:
            raise ValueError("Value must be a prime number.")
        for i in range(2, int(value**0.5) + 1):
            if value % i == 0:
                raise ValueError("Value is not a prime number.")


class IsPowerOfTwo(FieldConstraint[IntegerFieldValue]):
    def __call__(self, value: IntegerFieldValue) -> None:
        value = value
        if value <= 0 or (value & (value - 1)) != 0:
            raise ValueError("Value must be a power of two.")


class IsNonNegativeInteger(FieldConstraint[IntegerFieldValue]):
    def __call__(self, value: IntegerFieldValue) -> None:
        if value < 0:
            raise ValueError("Value must be a non-negative integer.")


## String FieldConstraint
class IsAlpha(FieldConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.isalpha():
            raise ValueError("String must contain only alphabetic characters.")


class IsDigit(FieldConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.isdigit():
            raise ValueError("String must contain only digits.")


class IsAlnum(FieldConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.isalnum():
            raise ValueError("String must contain only alphanumeric characters.")


class IsLower(FieldConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.islower():
            raise ValueError("String must be lowercase.")


class IsUpper(FieldConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.isupper():
            raise ValueError("String must be uppercase.")


class IsTitle(FieldConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.istitle():
            raise ValueError("String must be title-cased.")


class IsPrintable(FieldConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.isprintable():
            raise ValueError("String must contain only printable characters.")


class IsAscii(FieldConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not all(ord(c) < 128 for c in value):
            raise ValueError("String must contain only ASCII characters.")


class MatchesRegex(FieldConstraint[StringFieldValue]):
    def __init__(self, pattern: str) -> None:
        self.regex = re.compile(pattern)

    def __call__(self, value: StringFieldValue) -> None:
        if not self.regex.fullmatch(value):
            raise ValueError(
                f"String does not match regex pattern: {self.regex.pattern}."
            )


class StartsWith(FieldConstraint[StringFieldValue]):
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def __call__(self, value: StringFieldValue) -> None:
        if not value.startswith(self.prefix):
            raise ValueError(f"String must start with '{self.prefix}'.")


class EndsWith(FieldConstraint[StringFieldValue]):
    def __init__(self, suffix: str) -> None:
        self.suffix = suffix

    def __call__(self, value: StringFieldValue) -> None:
        if not value.endswith(self.suffix):
            raise ValueError(f"String must end with '{self.suffix}'.")


class ContainsSubstring(FieldConstraint[StringFieldValue]):
    def __init__(self, substring: str) -> None:
        self.substring = substring

    def __call__(self, value: StringFieldValue) -> None:
        if self.substring not in value:
            raise ValueError(f"String must contain '{self.substring}'.")
