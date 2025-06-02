from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union

if TYPE_CHECKING:
    from confflow.core.fields import Field, FloatField, IntegerField, StringField

T = TypeVar("T", bound="Field[Any]")


## Base FieldConstraint
class FieldConstraint(ABC, Generic[T]):
    @abstractmethod
    def __call__(self, field: T) -> None: ...


## Numeric FieldConstraint
NumberField = Union["IntegerField", "FloatField"]


class NonNegative(FieldConstraint[NumberField]):
    def __call__(self, field: NumberField) -> None:
        if field.value < 0:
            raise ValueError("Value must not be negative")


class IsPositive(FieldConstraint[NumberField]):
    def __call__(self, field: NumberField) -> None:
        if field.value <= 0:
            raise ValueError("Value must be positive (> 0)")


class IsNegative(FieldConstraint[NumberField]):
    def __call__(self, field: NumberField) -> None:
        if field.value >= 0:
            raise ValueError("Value must be negative (< 0)")


class NonZero(FieldConstraint[NumberField]):
    def __call__(self, field: NumberField) -> None:
        if field.value == 0:
            raise ValueError("Value must not be zero")


class GreaterThan(FieldConstraint[NumberField]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, field: NumberField) -> None:
        if field.value <= self._threshold:
            raise ValueError(f"Value must be greater than {self._threshold}")


class GreaterThanOrEqual(FieldConstraint[NumberField]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, field: NumberField) -> None:
        if field.value < self._threshold:
            raise ValueError(f"Value must be ≥ {self._threshold}")


class LessThan(FieldConstraint[NumberField]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, field: NumberField) -> None:
        if field.value >= self._threshold:
            raise ValueError(f"Value must be less than {self._threshold}")


class LessThanOrEqual(FieldConstraint[NumberField]):
    def __init__(self, threshold: float) -> None:
        self._threshold = threshold

    def __call__(self, field: NumberField) -> None:
        if field.value > self._threshold:
            raise ValueError(f"Value must be ≤ {self._threshold}")


class BetweenInclusive(FieldConstraint[NumberField]):
    def __init__(self, min_value: float, max_value: float) -> None:
        self._min_value = min_value
        self._max_value = max_value

    def __call__(self, field: NumberField) -> None:
        if not (self._min_value <= field.value <= self._max_value):
            raise ValueError(
                f"Value must be between {self._min_value} and {self._max_value} inclusive"
            )


class BetweenExclusive(FieldConstraint[NumberField]):
    def __init__(self, min_value: float, max_value: float) -> None:
        self._min_value = min_value
        self._max_value = max_value

    def __call__(self, field: NumberField) -> None:
        if not (self._min_value < field.value < self._max_value):
            raise ValueError(
                f"Value must be strictly between {self._min_value} and {self._max_value}"
            )


## Integer FieldConstraint
class IsEven(FieldConstraint["IntegerField"]):
    def __call__(self, field: "IntegerField") -> None:
        if field.value % 2 != 0:
            raise ValueError("Value must be even")


class IsOdd(FieldConstraint["IntegerField"]):
    def __call__(self, field: "IntegerField") -> None:
        if field.value % 2 != 1:
            raise ValueError("Value must be odd")


class MultipleOf(FieldConstraint["IntegerField"]):
    def __init__(self, base: int) -> None:
        if base == 0:
            raise ValueError("Base must not be zero")
        self.base = base

    def __call__(self, field: "IntegerField") -> None:
        if field.value % self.base != 0:
            raise ValueError(f"Value must be a multiple of {self.base}")


class Divides(FieldConstraint["IntegerField"]):
    def __init__(self, divisor: int) -> None:
        if divisor == 0:
            raise ValueError("Divisor must not be zero")
        self.divisor = divisor

    def __call__(self, field: "IntegerField") -> None:
        if field.value == 0 or self.divisor % field.value != 0:
            raise ValueError(f"{field.value} does not divide {self.divisor}")


class IsPrime(FieldConstraint["IntegerField"]):
    def __call__(self, field: "IntegerField") -> None:
        value = field.value
        if value < 2:
            raise ValueError("Value must be a prime number")
        for i in range(2, int(value**0.5) + 1):
            if value % i == 0:
                raise ValueError("Value is not a prime number")


class IsPowerOfTwo(FieldConstraint["IntegerField"]):
    def __call__(self, field: "IntegerField") -> None:
        value = field.value
        if value <= 0 or (value & (value - 1)) != 0:
            raise ValueError("Value must be a power of two")


class IsNonNegativeInteger(FieldConstraint["IntegerField"]):
    def __call__(self, field: "IntegerField") -> None:
        if field.value < 0:
            raise ValueError("Value must be a non-negative integer")


## String FieldConstraint
class IsAlpha(FieldConstraint["StringField"]):
    def __call__(self, field: "StringField") -> None:
        if not field.value.isalpha():
            raise ValueError("String must contain only alphabetic characters")


class IsDigit(FieldConstraint["StringField"]):
    def __call__(self, field: "StringField") -> None:
        if not field.value.isdigit():
            raise ValueError("String must contain only digits")


class IsAlnum(FieldConstraint["StringField"]):
    def __call__(self, field: "StringField") -> None:
        if not field.value.isalnum():
            raise ValueError("String must contain only alphanumeric characters")


class IsLower(FieldConstraint["StringField"]):
    def __call__(self, field: "StringField") -> None:
        if not field.value.islower():
            raise ValueError("String must be lowercase")


class IsUpper(FieldConstraint["StringField"]):
    def __call__(self, field: "StringField") -> None:
        if not field.value.isupper():
            raise ValueError("String must be uppercase")


class IsTitle(FieldConstraint["StringField"]):
    def __call__(self, field: "StringField") -> None:
        if not field.value.istitle():
            raise ValueError("String must be title-cased")


class IsPrintable(FieldConstraint["StringField"]):
    def __call__(self, field: "StringField") -> None:
        if not field.value.isprintable():
            raise ValueError("String must contain only printable characters")


class IsAscii(FieldConstraint["StringField"]):
    def __call__(self, field: "StringField") -> None:
        if not all(ord(c) < 128 for c in field.value):
            raise ValueError("String must contain only ASCII characters")


class MatchesRegex(FieldConstraint["StringField"]):
    def __init__(self, pattern: str) -> None:
        self.regex = re.compile(pattern)

    def __call__(self, field: "StringField") -> None:
        if not self.regex.fullmatch(field.value):
            raise ValueError(
                f"String does not match regex pattern: {self.regex.pattern}"
            )


class StartsWith(FieldConstraint["StringField"]):
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def __call__(self, field: "StringField") -> None:
        if not field.value.startswith(self.prefix):
            raise ValueError(f"String must start with '{self.prefix}'")


class EndsWith(FieldConstraint["StringField"]):
    def __init__(self, suffix: str) -> None:
        self.suffix = suffix

    def __call__(self, field: "StringField") -> None:
        if not field.value.endswith(self.suffix):
            raise ValueError(f"String must end with '{self.suffix}'")


class ContainsSubstring(FieldConstraint["StringField"]):
    def __init__(self, substring: str) -> None:
        self.substring = substring

    def __call__(self, field: "StringField") -> None:
        if self.substring not in field.value:
            raise ValueError(f"String must contain '{self.substring}'")
