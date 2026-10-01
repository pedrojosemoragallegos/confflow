from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, ClassVar

from confflow.core.constraints.local_date import Range
from confflow.core.definitions.base import Definition

if TYPE_CHECKING:
    from confflow.core.constraints.base import Constraint


class LocalDate(Definition[date]):
    VALUE_TYPE: ClassVar[type[date]] = date

    def __init__(
        self,
        *constraints: Constraint[date],
        minimum: date | None = None,
        maximum: date | None = None,
    ) -> None:
        constraints: list[Constraint[date]] = list(constraints)

        if minimum is not None or maximum is not None:
            constraints.append(Range(minimum=minimum, maximum=maximum))

        # Reverse the constraints to maintain the intended order
        super().__init__(*reversed(constraints))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(constraints={self.constraints!r})"
