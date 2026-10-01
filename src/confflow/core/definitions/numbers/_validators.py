from __future__ import annotations

from math import isnan

from confflow.core.definitions.exceptions import ValidationError


def validate_integer(label: str, /, *, value: int) -> None:
    if type(value) is not int:
        raise ValidationError(f"{label} must be an integer")


def validate_non_nan_float(label: str, /, *, value: float) -> None:
    if isnan(value):
        raise ValidationError(f"{label} cannot be NaN")


def validate_float(label: str, /, *, value: float) -> None:
    if type(value) is not float:
        raise ValidationError(f"{label} must be a float")


def validate_integer_bounds(
    label: str,
    /,
    *,
    minimum: int,
    maximum: int,
) -> None:
    if minimum > maximum:
        raise ValidationError(f"{label} minimum cannot exceed maximum")


def validate_float_bounds(
    label: str,
    /,
    *,
    minimum: float,
    maximum: float,
) -> None:
    if minimum > maximum:
        raise ValidationError(f"{label} minimum cannot exceed maximum")


def validate_toml_integer(*, value: int, minimum: int, maximum: int) -> None:
    if value < minimum or value > maximum:
        raise ValidationError(
            "integer constraint is outside the TOML signed 64-bit range"
        )
