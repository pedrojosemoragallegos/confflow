from __future__ import annotations

from datetime import time
from typing import Final

from typing_extensions import override

from ..exceptions import InvalidValueError
from ._validation import (
    _is_aware_time,
    _validate_optional_local_time,
    _validate_time_bounds,
)
from .scalar import Scalar


class LocalTime(Scalar[time]):
    __slots__ = ("_maximum", "_minimum")

    @override
    def __init__(
        self,
        name: str,
        description: str = "",
        /,
        *,
        required: bool = False,
        default: time | None = None,
        minimum: time | None = None,
        maximum: time | None = None,
    ) -> None:
        _validate_optional_local_time(minimum, "minimum")
        _validate_optional_local_time(maximum, "maximum")
        _validate_time_bounds(minimum, maximum, "local time")
        self._minimum: Final[time | None] = minimum
        self._maximum: Final[time | None] = maximum
        super().__init__(name, description, required=required, default=default)

    @property
    @override
    def value_type(self) -> type[time]:
        return time

    @override
    def validate(self, value: object, path: tuple[str | int, ...]) -> None:
        if type(value) is not time or _is_aware_time(value):
            raise InvalidValueError("expected a timezone-naive time", path)
        if (minimum := self._minimum) is not None and value < minimum:
            raise InvalidValueError("time is smaller than the minimum", path)
        if (maximum := self._maximum) is not None and value > maximum:
            raise InvalidValueError("time exceeds the maximum", path)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, required={self.required!r}, "
            f"default={self.default!r}, "
            f"minimum={self._minimum!r}, maximum={self._maximum!r})"
        )
