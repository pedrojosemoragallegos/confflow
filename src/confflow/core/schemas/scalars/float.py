from __future__ import annotations

from typing import TYPE_CHECKING

from confflow.core.constraints.literal import Literal
from confflow.core.definitions import Float as FloatDefinition

from .base import Scalar

if TYPE_CHECKING:
    from collections.abc import Sequence

    from confflow.core.constraints import Constraint


class Float(Scalar[float]):
    def __init__(
        self,
        name: str,
        description: str,
        /,
        *constraints: Constraint[float],
        optional: bool = False,
        default: float | None = None,
        minimum: float | None = None,
        maximum: float | None = None,
        literal: Sequence[float] | None = None,
    ) -> None:
        literal_constraint: tuple[()] | tuple[Literal[float]] = (
            () if literal is None else (Literal(*literal),)
        )

        super().__init__(
            name,
            description,
            optional=optional,
            definition=FloatDefinition(
                *constraints,
                *literal_constraint,
                minimum=minimum,
                maximum=maximum,
            ),
            default=default,
        )
