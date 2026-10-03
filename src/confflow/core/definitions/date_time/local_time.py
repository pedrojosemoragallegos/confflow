from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING, final

from confflow.core.definitions.base import Definition
from confflow.core.definitions.constraints.local_time import Range

if TYPE_CHECKING:
    from confflow.core.definitions.constraints import Constraint


@final
class LocalTime(Definition[time]):
    def __init__(
        self,
        *constraints: Constraint[time],
        minimum: time | None = None,
        maximum: time | None = None,
    ) -> None:
        constraints: list[Constraint[time]] = list(constraints)

        if minimum is not None or maximum is not None:
            constraints.append(Range(minimum=minimum, maximum=maximum))

        # Reverse the constraints to maintain the intended order
        super().__init__(*reversed(constraints))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(constraints={self.constraints!r})"
