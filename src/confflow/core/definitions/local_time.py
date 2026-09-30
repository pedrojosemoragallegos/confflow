from __future__ import annotations

from datetime import time
from typing import ClassVar, Final

from typing_extensions import override

from ._validators import (
    is_aware_time,
    validate_local_time,
    validate_time_bounds,
)
from .base import Definition
from .exceptions import DefinitionError


class LocalTime(Definition[time]):
    __slots__ = ("__maximum", "__minimum")

    VALUE_TYPE: ClassVar[type[time]] = time

    @override
    def __init__(
        self,
        *,
        minimum: time | None = None,
        maximum: time | None = None,
    ) -> None:
        if minimum is not None:
            validate_local_time(value=minimum, label="minimum")

        if maximum is not None:
            validate_local_time(value=maximum, label="maximum")

        if minimum is not None and maximum is not None:
            validate_time_bounds(minimum=minimum, maximum=maximum, label="local time")

        self.__minimum: Final[time | None] = minimum
        self.__maximum: Final[time | None] = maximum

    @override
    def validate(self, value: object) -> None:
        if type(value) is not time or is_aware_time(value):
            raise DefinitionError("expected a timezone-naive time")

        if (minimum := self.__minimum) is not None and value < minimum:
            raise DefinitionError("time is smaller than the minimum")

        if (maximum := self.__maximum) is not None and value > maximum:
            raise DefinitionError("time exceeds the maximum")

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, maximum={self.__maximum!r})"
        )
