from __future__ import annotations

from datetime import date, datetime, time

from confflow.core.definitions.exceptions import ValidationError


def validate_datetime_bounds(
    label: str, /, *, minimum: datetime, maximum: datetime
) -> None:
    if minimum > maximum:
        raise ValidationError(f"{label} minimum cannot exceed maximum")


def validate_date_bounds(label: str, /, *, minimum: date, maximum: date) -> None:
    if minimum > maximum:
        raise ValidationError(f"{label} minimum cannot exceed maximum")


def validate_time_bounds(label: str, /, *, minimum: time, maximum: time) -> None:
    if minimum > maximum:
        raise ValidationError(f"{label} minimum cannot exceed maximum")


def validate_offset_datetime(label: str, /, *, value: datetime) -> None:
    if type(value) is not datetime or not is_aware_datetime(value):
        raise ValidationError(f"{label} must be a timezone-aware datetime")


def validate_local_datetime(label: str, /, *, value: datetime) -> None:
    if type(value) is not datetime or is_aware_datetime(value):
        raise ValidationError(f"{label} must be a timezone-naive datetime")


def validate_local_date(label: str, /, *, value: date) -> None:
    if type(value) is not date:
        raise ValidationError(f"{label} must be a date")


def validate_local_time(label: str, /, *, value: time) -> None:
    if type(value) is not time or is_aware_time(value):
        raise ValidationError(f"{label} must be a timezone-naive time")


def is_aware_datetime(value: datetime, /) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


def is_aware_time(value: time, /) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


def validate_toml_integer(*, value: int, minimum: int, maximum: int) -> None:
    if value < minimum or value > maximum:
        raise ValidationError(
            "integer constraint is outside the TOML signed 64-bit range"
        )
