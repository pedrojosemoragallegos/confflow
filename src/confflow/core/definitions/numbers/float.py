from __future__ import annotations

from typing import TYPE_CHECKING, final

from confflow.core.definitions.base import Definition
from confflow.core.definitions.constraints.float import NotNaN, Range

if TYPE_CHECKING:
    from confflow.core.definitions.constraints import Constraint


@final
class Float(Definition[float]):
    def __init__(
        self,
        *constraints: Constraint[float],
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> None:
        constraints: list[Constraint[float]] = list(constraints)

        constraints.append(NotNaN())

        if minimum is not None or maximum is not None:
            constraints.append(Range(minimum=minimum, maximum=maximum))

        # Reverse the constraints to maintain the intended order
        super().__init__(*list(reversed(constraints)))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(constraints={self.constraints!r})"
