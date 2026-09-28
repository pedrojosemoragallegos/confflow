from __future__ import annotations

from datetime import date, datetime, time
from math import isnan

from ..exceptions import SchemaError


def _validate_optional_non_negative_integer(value: int | None, label: str) -> None:
    if value is not None and (type(value) is not int or value < 0):
        raise SchemaError(f"{label} must be a non-negative integer")


def _validate_optional_integer(value: int | None, label: str) -> None:
    if value is not None and type(value) is not int:
        raise SchemaError(f"{label} must be an integer")


def _validate_optional_float(value: float | None, label: str) -> None:
    if value is not None and type(value) is not float:
        raise SchemaError(f"{label} must be a float")


def _validate_non_nan_float(value: float | None, label: str) -> None:
    if value is not None and isnan(value):
        raise SchemaError(f"{label} cannot be NaN")


def _validate_integer_bounds(
    minimum: int | None, maximum: int | None, label: str
) -> None:
    if minimum is not None and maximum is not None and minimum > maximum:
        raise SchemaError(f"{label} minimum cannot exceed maximum")


def _validate_float_bounds(
    minimum: float | None, maximum: float | None, label: str
) -> None:
    if minimum is not None and maximum is not None and minimum > maximum:
        raise SchemaError(f"{label} minimum cannot exceed maximum")


def _validate_datetime_bounds(
    minimum: datetime | None, maximum: datetime | None, label: str
) -> None:
    if minimum is not None and maximum is not None and minimum > maximum:
        raise SchemaError(f"{label} minimum cannot exceed maximum")


def _validate_date_bounds(
    minimum: date | None, maximum: date | None, label: str
) -> None:
    if minimum is not None and maximum is not None and minimum > maximum:
        raise SchemaError(f"{label} minimum cannot exceed maximum")


def _validate_time_bounds(
    minimum: time | None, maximum: time | None, label: str
) -> None:
    if minimum is not None and maximum is not None and minimum > maximum:
        raise SchemaError(f"{label} minimum cannot exceed maximum")


def _validate_optional_offset_datetime(value: datetime | None, label: str) -> None:
    if value is not None and (
        type(value) is not datetime or not _is_aware_datetime(value)
    ):
        raise SchemaError(f"{label} must be a timezone-aware datetime")


def _validate_optional_local_datetime(value: datetime | None, label: str) -> None:
    if value is not None and (type(value) is not datetime or _is_aware_datetime(value)):
        raise SchemaError(f"{label} must be a timezone-naive datetime")


def _validate_optional_local_date(value: date | None, label: str) -> None:
    if value is not None and type(value) is not date:
        raise SchemaError(f"{label} must be a date")


def _validate_optional_local_time(value: time | None, label: str) -> None:
    if value is not None and (type(value) is not time or _is_aware_time(value)):
        raise SchemaError(f"{label} must be a timezone-naive time")


def _is_aware_datetime(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


def _is_aware_time(value: time) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


def _validate_toml_integer(value: int | None, minimum: int, maximum: int) -> None:
    if value is None:
        return
    if value < minimum or value > maximum:
        raise SchemaError("integer constraint is outside the TOML signed 64-bit range")
