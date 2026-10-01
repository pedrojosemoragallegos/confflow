from __future__ import annotations

from .exceptions import ValidationError


def validate_integer_bounds(label: str, /, *, minimum: int, maximum: int) -> None:
    if minimum > maximum:
        raise ValidationError(f"{label} minimum cannot exceed maximum")


def validate_float_bounds(label: str, /, *, minimum: float, maximum: float) -> None:
    if minimum > maximum:
        raise ValidationError(f"{label} minimum cannot exceed maximum")


def validate_non_negative_integer(label: str, /, *, value: int) -> None:
    if type(value) is not int or value < 0:
        raise ValidationError(f"{label} must be a non-negative integer")


def validate_toml_integer(
    label: str, /, *, value: int, minimum: int, maximum: int
) -> None:
    if value < minimum or value > maximum:
        raise ValidationError(
            f"{label} integer constraint is outside the TOML signed 64-bit range"
        )
