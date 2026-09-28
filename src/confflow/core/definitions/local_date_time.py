from __future__ import annotations

from datetime import datetime
from typing import Final

from typing_extensions import override

from ..exceptions import InvalidValueError
from ._validation import (
    _is_aware_datetime,
    _validate_datetime_bounds,
    _validate_optional_local_datetime,
)
from .scalar import Scalar


class LocalDateTime(Scalar[datetime]):
    __slots__ = ("_maximum", "_minimum")

    @override
    def __init__(
        self,
        name: str,
        description: str = "",
        /,
        *,
        required: bool = False,
        default: datetime | None = None,
        minimum: datetime | None = None,
        maximum: datetime | None = None,
    ) -> None:
        _validate_optional_local_datetime(minimum, "minimum")
        _validate_optional_local_datetime(maximum, "maximum")
        _validate_datetime_bounds(minimum, maximum, "local date-time")
        self._minimum: Final[datetime | None] = minimum
        self._maximum: Final[datetime | None] = maximum
        super().__init__(name, description, required=required, default=default)

    @property
    @override
    def value_type(self) -> type[datetime]:
        return datetime

    @override
    def validate(self, value: object, path: tuple[str | int, ...]) -> None:
        if type(value) is not datetime or _is_aware_datetime(value):
            raise InvalidValueError("expected a timezone-naive datetime", path)
        if (minimum := self._minimum) is not None and value < minimum:
            raise InvalidValueError("date-time is smaller than the minimum", path)
        if (maximum := self._maximum) is not None and value > maximum:
            raise InvalidValueError("date-time exceeds the maximum", path)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, required={self.required!r}, "
            f"default={self.default!r}, "
            f"minimum={self._minimum!r}, maximum={self._maximum!r})"
        )
