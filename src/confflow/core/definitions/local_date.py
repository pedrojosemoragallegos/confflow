from __future__ import annotations

from datetime import date
from typing import ClassVar, Final

from typing_extensions import override

from ._validators import validate_date_bounds, validate_local_date
from .base import Definition
from .exceptions import DefinitionError


class LocalDate(Definition[date]):
    __slots__ = ("__maximum", "__minimum")

    VALUE_TYPE: ClassVar[type[date]] = date

    @override
    def __init__(
        self,
        *,
        minimum: date | None = None,
        maximum: date | None = None,
    ) -> None:
        if minimum is not None:
            validate_local_date(value=minimum, label="minimum")

        if maximum is not None:
            validate_local_date(value=maximum, label="maximum")

        if minimum is not None and maximum is not None:
            validate_date_bounds(minimum=minimum, maximum=maximum, label="local date")

        self.__minimum: Final[date | None] = minimum
        self.__maximum: Final[date | None] = maximum

    @override
    def validate(self, value: object) -> None:
        if type(value) is not date:
            raise DefinitionError("expected a date")

        if (minimum := self.__minimum) is not None and value < minimum:
            raise DefinitionError("date is smaller than the minimum")

        if (maximum := self.__maximum) is not None and value > maximum:
            raise DefinitionError("date exceeds the maximum")

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, maximum={self.__maximum!r})"
        )
