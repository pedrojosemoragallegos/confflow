from __future__ import annotations

from datetime import date, datetime, time
from math import isnan
from typing import TYPE_CHECKING, ClassVar, Final, Generic, TypeVar, cast

from typing_extensions import override

from ..exceptions import InvalidValueError, SchemaError
from ._validation import _is_aware_datetime, _is_aware_time, _validate_toml_integer
from .base import TomlScalar
from .scalar import Scalar

if TYPE_CHECKING:
    from collections.abc import Iterable

LiteralValueT = TypeVar("LiteralValueT", bound=TomlScalar)
_MINIMUM_LITERAL_VALUES = 2


def _validate_datetime_literal_values(datetime_values: tuple[datetime, ...]) -> bool:
    awareness_values = tuple(_is_aware_datetime(value) for value in datetime_values)
    resolved_datetime_awareness = awareness_values[0]
    if any(
        awareness is not resolved_datetime_awareness for awareness in awareness_values
    ):
        msg = "literal datetime values cannot mix offset and local date-times"
        raise SchemaError(msg)
    return resolved_datetime_awareness


def _validate_scalar_type_values(
    value_type: type[object], value_tuple: tuple[TomlScalar, ...]
) -> bool | None:
    if value_type is int:
        for value in cast("tuple[int, ...]", value_tuple):
            _validate_toml_integer(value, -(2**63), (2**63) - 1)
        return None
    if value_type is float:
        if any(isnan(value) for value in cast("tuple[float, ...]", value_tuple)):
            raise SchemaError("literal decimal values cannot contain NaN")
        return None
    if value_type is datetime:
        return _validate_datetime_literal_values(
            cast("tuple[datetime, ...]", value_tuple)
        )
    if value_type is time:
        if any(
            _is_aware_time(value) for value in cast("tuple[time, ...]", value_tuple)
        ):
            raise SchemaError("TOML literal time values must be timezone-naive")
        return None
    if value_type is not str and value_type is not bool and value_type is not date:
        raise SchemaError("literal values must use a TOML scalar type")
    return None


class Literal(Scalar[LiteralValueT], Generic[LiteralValueT]):
    __slots__ = ("_datetime_is_aware", "_value_type", "_values")

    _EXPECTED_TYPE: ClassVar[type[object] | None] = None
    _DATETIME_IS_AWARE: ClassVar[bool | None] = None

    @override
    def __init__(  # ty: ignore[invalid-method-override]
        self,
        name: str,
        description: str = "",
        /,
        *,
        values: Iterable[LiteralValueT],
        required: bool = False,
        default: LiteralValueT | None = None,
    ) -> None:
        if isinstance(values, (str, bytes, bytearray)):
            raise SchemaError(
                "literal values must be an iterable of TOML scalar values"
            )

        value_tuple = tuple(values)
        if len(value_tuple) < _MINIMUM_LITERAL_VALUES:
            raise SchemaError("literal must contain at least two values")

        value_type = type(value_tuple[0])
        if self._EXPECTED_TYPE is not None and value_type is not self._EXPECTED_TYPE:
            raise SchemaError(
                f"literal values must be {self._EXPECTED_TYPE.__name__} values"
            )
        if any(type(value) is not value_type for value in value_tuple):
            raise SchemaError("literal values must all have the same TOML scalar type")

        resolved_datetime_awareness = _validate_scalar_type_values(
            value_type, cast("tuple[TomlScalar, ...]", value_tuple)
        )
        if (
            value_type is datetime
            and self._DATETIME_IS_AWARE is not None
            and resolved_datetime_awareness is not self._DATETIME_IS_AWARE
        ):
            expected = "timezone-aware" if self._DATETIME_IS_AWARE else "timezone-naive"
            raise SchemaError(f"literal values must be {expected} datetimes")

        if self._DATETIME_IS_AWARE is not None and value_type is not datetime:
            raise SchemaError(
                "datetime awareness can only be specified for datetime literals"
            )
        if len(set(value_tuple)) != len(value_tuple):
            raise SchemaError("literal values cannot contain duplicates")

        self._values: Final[tuple[LiteralValueT, ...]] = value_tuple
        self._value_type: Final[type[TomlScalar]] = cast("type[TomlScalar]", value_type)
        self._datetime_is_aware: Final[bool | None] = resolved_datetime_awareness
        super().__init__(name, description, required=required, default=default)

    @property
    @override
    def value_type(self) -> type[TomlScalar]:
        return self._value_type

    @override
    def validate(self, value: object, path: tuple[str | int, ...]) -> None:
        if type(value) is not self._value_type:
            raise InvalidValueError(
                "value does not use the literal's TOML scalar type", path
            )
        if self._value_type is float and isnan(cast("float", value)):
            raise InvalidValueError("NaN is not allowed", path)
        if (
            self._value_type is datetime
            and _is_aware_datetime(cast("datetime", value))
            is not self._datetime_is_aware
        ):
            raise InvalidValueError(
                "date-time does not use the literal's date-time kind", path
            )
        if value not in self._values:
            raise InvalidValueError("value is not one of the literal values", path)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, required={self.required!r}, "
            f"default={self.default!r}, values={self._values!r})"
        )
