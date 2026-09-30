from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, ClassVar, cast

from typing_extensions import override

from ...exceptions import SchemaError
from ._validators import validate_datetime_values
from .base import Literal

if TYPE_CHECKING:
    from ..base import Value as ScalarValue


class LocalDateTimeLiteral(Literal[datetime]):
    __slots__ = ()

    VALUE_TYPE: ClassVar[type[datetime]] = datetime

    @override
    def _validate_literal_values(self, values: tuple[ScalarValue, ...]) -> None:
        awareness: bool = validate_datetime_values(
            datetime_values=cast(typ="tuple[datetime, ...]", val=values)
        )

        if awareness:
            raise SchemaError("literal values must be timezone-naive datetimes")
