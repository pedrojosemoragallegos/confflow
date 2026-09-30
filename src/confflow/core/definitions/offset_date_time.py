from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Final

from typing_extensions import override

from ._validators import (
    is_aware_datetime,
    validate_datetime_bounds,
    validate_offset_datetime,
)
from .base import Definition
from .exceptions import DefinitionError


class OffsetDateTime(Definition[datetime]):
    __slots__ = ("__maximum", "__minimum")

    VALUE_TYPE: ClassVar[type[datetime]] = datetime

    @override
    def __init__(
        self,
        *,
        minimum: datetime | None = None,
        maximum: datetime | None = None,
    ) -> None:
        if minimum is not None:
            validate_offset_datetime(value=minimum, label="minimum")

        if maximum is not None:
            validate_offset_datetime(value=maximum, label="maximum")

        if minimum is not None and maximum is not None:
            validate_datetime_bounds(
                minimum=minimum, maximum=maximum, label="offset date-time"
            )

        self.__minimum: Final[datetime | None] = minimum
        self.__maximum: Final[datetime | None] = maximum

    @override
    def validate(self, value: object) -> None:
        if type(value) is not datetime or not is_aware_datetime(value):
            raise DefinitionError("expected a timezone-aware datetime")

        if (minimum := self.__minimum) is not None and value < minimum:
            raise DefinitionError("date-time is smaller than the minimum")

        if (maximum := self.__maximum) is not None and value > maximum:
            raise DefinitionError("date-time exceeds the maximum")

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, maximum={self.__maximum!r})"
        )
