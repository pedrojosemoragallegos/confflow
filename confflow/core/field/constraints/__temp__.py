import re
import uuid
from typing import Generic, Pattern as RegexPattern, TypeVar, Union

T = TypeVar("T")


# Base Constraint
class Constraint(Generic[T]):
    def validate(self, value: T) -> None:
        raise NotImplementedError("Subclasses must implement `validate`.")


# ==== STR CONSTRAINTS ====


class MinLength(Constraint[str]):
    def __init__(self, min_length: int):
        self.min_length = min_length

    def validate(self, value: str) -> None:
        if len(value) < self.min_length:
            raise ValueError(
                f"Length must be at least {self.min_length}, got {len(value)}."
            )


class MaxLength(Constraint[str]):
    def __init__(self, max_length: int):
        self.max_length = max_length

    def validate(self, value: str) -> None:
        if len(value) > self.max_length:
            raise ValueError(
                f"Length must be at most {self.max_length}, got {len(value)}."
            )


class Pattern(Constraint[str]):
    def __init__(self, pattern: str):
        self.pattern: RegexPattern = re.compile(pattern)

    def validate(self, value: str) -> None:
        if not self.pattern.fullmatch(value):
            raise ValueError(
                f"Value '{value}' does not match pattern '{self.pattern.pattern}'."
            )


class StartsWith(Constraint[str]):
    def __init__(self, prefix: str):
        self.prefix = prefix

    def validate(self, value: str) -> None:
        if not value.startswith(self.prefix):
            raise ValueError(f"Value must start with '{self.prefix}'.")


class EndsWith(Constraint[str]):
    def __init__(self, suffix: str):
        self.suffix = suffix

    def validate(self, value: str) -> None:
        if not value.endswith(self.suffix):
            raise ValueError(f"Value must end with '{self.suffix}'.")


class Contains(Constraint[str]):
    def __init__(self, substring: str):
        self.substring = substring

    def validate(self, value: str) -> None:
        if self.substring not in value:
            raise ValueError(f"Value must contain '{self.substring}'.")


class IsLower(Constraint[str]):
    def validate(self, value: str) -> None:
        if not value.islower():
            raise ValueError("Value must be lowercase.")


class IsUpper(Constraint[str]):
    def validate(self, value: str) -> None:
        if not value.isupper():
            raise ValueError("Value must be uppercase.")


class IsEmail(Constraint[str]):
    def validate(self, value: str) -> None:
        email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        if not email_pattern.fullmatch(value):
            raise ValueError("Value must be a valid email address.")


class IsUUID(Constraint[str]):
    def validate(self, value: str) -> None:
        try:
            uuid.UUID(value)
        except ValueError:
            raise ValueError("Value must be a valid UUID.")


# ==== INT / FLOAT CONSTRAINTS ====

Numeric = Union[int, float]


class MinValue(Constraint[Numeric]):
    def __init__(self, minimum: Numeric):
        self.minimum = minimum

    def validate(self, value: Numeric) -> None:
        if value < self.minimum:
            raise ValueError(f"Value must be ≥ {self.minimum}, got {value}.")


class MaxValue(Constraint[Numeric]):
    def __init__(self, maximum: Numeric):
        self.maximum = maximum

    def validate(self, value: Numeric) -> None:
        if value > self.maximum:
            raise ValueError(f"Value must be ≤ {self.maximum}, got {value}.")


class GreaterThan(Constraint[Numeric]):
    def __init__(self, threshold: Numeric):
        self.threshold = threshold

    def validate(self, value: Numeric) -> None:
        if value <= self.threshold:
            raise ValueError(f"Value must be > {self.threshold}, got {value}.")


class LessThan(Constraint[Numeric]):
    def __init__(self, threshold: Numeric):
        self.threshold = threshold

    def validate(self, value: Numeric) -> None:
        if value >= self.threshold:
            raise ValueError(f"Value must be < {self.threshold}, got {value}.")


class MultipleOf(Constraint[Numeric]):
    def __init__(self, base: Numeric):
        self.base = base

    def validate(self, value: Numeric) -> None:
        if value % self.base != 0:
            raise ValueError(f"Value must be a multiple of {self.base}, got {value}.")


class IsPositive(Constraint[Numeric]):
    def validate(self, value: Numeric) -> None:
        if value <= 0:
            raise ValueError("Value must be positive.")


class IsNegative(Constraint[Numeric]):
    def validate(self, value: Numeric) -> None:
        if value >= 0:
            raise ValueError("Value must be negative.")


class IsNonZero(Constraint[Numeric]):
    def validate(self, value: Numeric) -> None:
        if value == 0:
            raise ValueError("Value must not be zero.")


# ==== BOOL CONSTRAINTS ====


class IsTrue(Constraint[bool]):
    def validate(self, value: bool) -> None:
        if value is not True:
            raise ValueError("Value must be True.")


class IsFalse(Constraint[bool]):
    def validate(self, value: bool) -> None:
        if value is not False:
            raise ValueError("Value must be False.")
