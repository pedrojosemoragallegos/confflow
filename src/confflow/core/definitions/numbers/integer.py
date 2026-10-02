from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from confflow.core.definitions.base import Definition
from confflow.core.definitions.constraints.integer import Range

if TYPE_CHECKING:
    from confflow.core.definitions.constraints import Constraint


class Integer(Definition[int]):
    VALUE_TYPE: ClassVar[type[int]] = int

    def __init__(
        self,
        *constraints: Constraint[int],
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> None:
        constraints: list[Constraint[int]] = list(constraints)

        constraints.append(Range(minimum=minimum, maximum=maximum))

        # Reverse the constraints to maintain the intended order
        super().__init__(*reversed(constraints))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(constraints={self.constraints!r})"
