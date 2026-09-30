from __future__ import annotations

from datetime import date, datetime, time
from math import isnan
from re import Pattern, compile as compile_pattern
from typing import Final

from ..exceptions import SchemaError

_NAME_PATTERN: Final[Pattern[str]] = compile_pattern(pattern=r"[A-Za-z0-9_-]+")


def validate_name(*, value: object, label: str) -> None:
    if type(value) is not str or _NAME_PATTERN.fullmatch(string=value) is None:
        raise SchemaError(
            f"{label} must contain only ASCII letters, digits, '_' or '-'"
        )


def validate_non_negative_integer(*, value: int, label: str) -> None:
    if type(value) is not int or value < 0:
        raise SchemaError(f"{label} must be a non-negative integer")


def validate_integer(*, value: int, label: str) -> None:
    if type(value) is not int:
        raise SchemaError(f"{label} must be an integer")


def validate_float(*, value: float, label: str) -> None:
    if type(value) is not float:
        raise SchemaError(f"{label} must be a float")


def validate_non_nan_float(*, value: float, label: str) -> None:
    if isnan(value):
        raise SchemaError(f"{label} cannot be NaN")


def validate_integer_bounds(
    *,
    minimum: int,
    maximum: int,
    label: str,
) -> None:
    if minimum > maximum:
        raise SchemaError(f"{label} minimum cannot exceed maximum")


def validate_float_bounds(
    *,
    minimum: float,
    maximum: float,
    label: str,
) -> None:
    if minimum > maximum:
        raise SchemaError(f"{label} minimum cannot exceed maximum")


def validate_datetime_bounds(
    *,
    minimum: datetime,
    maximum: datetime,
    label: str,
) -> None:
    if minimum > maximum:
        raise SchemaError(f"{label} minimum cannot exceed maximum")


def validate_date_bounds(
    *,
    minimum: date,
    maximum: date,
    label: str,
) -> None:
    if minimum > maximum:
        raise SchemaError(f"{label} minimum cannot exceed maximum")


def validate_time_bounds(
    *,
    minimum: time,
    maximum: time,
    label: str,
) -> None:
    if minimum > maximum:
        raise SchemaError(f"{label} minimum cannot exceed maximum")


def validate_offset_datetime(*, value: datetime, label: str) -> None:
    if type(value) is not datetime or not is_aware_datetime(value):
        raise SchemaError(f"{label} must be a timezone-aware datetime")


def validate_local_datetime(*, value: datetime, label: str) -> None:
    if type(value) is not datetime or is_aware_datetime(value):
        raise SchemaError(f"{label} must be a timezone-naive datetime")


def validate_local_date(*, value: date, label: str) -> None:
    if type(value) is not date:
        raise SchemaError(f"{label} must be a date")


def validate_local_time(*, value: time, label: str) -> None:
    if type(value) is not time or is_aware_time(value):
        raise SchemaError(f"{label} must be a timezone-naive time")


def is_aware_datetime(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


def is_aware_time(value: time) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


def validate_toml_integer(*, value: int, minimum: int, maximum: int) -> None:
    if value < minimum or value > maximum:
        raise SchemaError("integer constraint is outside the TOML signed 64-bit range")
