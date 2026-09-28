from __future__ import annotations

from datetime import date
from typing import Final

from typing_extensions import override

from ..exceptions import InvalidValueError
from ._validation import _validate_date_bounds, _validate_optional_local_date
from .scalar import Scalar


class LocalDate(Scalar[date]):
    __slots__ = ("_maximum", "_minimum")

    @override
    def __init__(
        self,
        name: str,
        description: str = "",
        /,
        *,
        required: bool = False,
        default: date | None = None,
        minimum: date | None = None,
        maximum: date | None = None,
    ) -> None:
        _validate_optional_local_date(minimum, "minimum")
        _validate_optional_local_date(maximum, "maximum")
        _validate_date_bounds(minimum, maximum, "local date")
        self._minimum: Final[date | None] = minimum
        self._maximum: Final[date | None] = maximum
        super().__init__(name, description, required=required, default=default)

    @property
    @override
    def value_type(self) -> type[date]:
        return date

    @override
    def validate(self, value: object, path: tuple[str | int, ...]) -> None:
        if type(value) is not date:
            raise InvalidValueError("expected a date", path)
        if (minimum := self._minimum) is not None and value < minimum:
            raise InvalidValueError("date is smaller than the minimum", path)
        if (maximum := self._maximum) is not None and value > maximum:
            raise InvalidValueError("date exceeds the maximum", path)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, required={self.required!r}, "
            f"default={self.default!r}, "
            f"minimum={self._minimum!r}, maximum={self._maximum!r})"
        )
