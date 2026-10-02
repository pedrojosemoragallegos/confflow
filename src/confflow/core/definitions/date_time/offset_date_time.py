from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, ClassVar

from confflow.core.definitions.base import Definition
from confflow.core.definitions.constraints.offset_date_time import Range

if TYPE_CHECKING:
    from confflow.core.definitions.constraints import Constraint


class OffsetDateTime(Definition[datetime]):
    VALUE_TYPE: ClassVar[type[datetime]] = datetime

    def __init__(
        self,
        *constraints: Constraint[datetime],
        minimum: datetime | None = None,
        maximum: datetime | None = None,
    ) -> None:
        constraints: list[Constraint[datetime]] = list(constraints)

        if minimum is not None or maximum is not None:
            constraints.append(Range(minimum=minimum, maximum=maximum))

        # Reverse the constraints to maintain the intended order
        super().__init__(*reversed(constraints))

    def validate(self, value: datetime, /) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("expected a timezone-aware datetime")

        super().validate(value)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(constraints={self.constraints!r})"
