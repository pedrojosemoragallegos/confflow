from __future__ import annotations

from datetime import date, datetime, time
from math import isnan
from typing import TYPE_CHECKING, cast

from ...exceptions import SchemaError
from .._validators import is_aware_datetime, is_aware_time, validate_toml_integer

if TYPE_CHECKING:
    from ..base import Value as ScalarValue


def validate_datetime_values(datetime_values: tuple[datetime, ...]) -> bool:
    awareness_values: tuple[bool, ...] = tuple(
        is_aware_datetime(value) for value in datetime_values
    )

    if any(awareness is not awareness_values[0] for awareness in awareness_values):
        msg = "literal datetime values cannot mix offset and local date-times"
        raise SchemaError(msg)

    return awareness_values[0]


def validate_scalar_type_values(
    value_type: type[object],
    value_tuple: tuple[ScalarValue, ...],
) -> bool | None:
    if value_type is int:
        for value in cast(typ="tuple[int, ...]", val=value_tuple):
            validate_toml_integer(value=value, minimum=-(2**63), maximum=(2**63) - 1)
        return None

    if value_type is float:
        if any(
            isnan(value) for value in cast(typ="tuple[float, ...]", val=value_tuple)
        ):
            raise SchemaError("literal decimal values cannot contain NaN")
        return None

    if value_type is datetime:
        return None

    if value_type is time:
        if any(is_aware_time(value) for value in cast("tuple[time, ...]", value_tuple)):
            raise SchemaError("TOML literal time values must be timezone-naive")
        return None

    if value_type is not str and value_type is not bool and value_type is not date:
        raise SchemaError("literal values must use a TOML scalar type")
    return None
