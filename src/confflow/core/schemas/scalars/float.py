from __future__ import annotations

from typing import TYPE_CHECKING

from confflow.core.definitions import Float as FloatDefinition
from confflow.core.definitions.constraints.literal import Literal

from .base import Scalar

if TYPE_CHECKING:
    from collections.abc import Sequence

    from confflow.core.definitions.constraints import Constraint


class Float(Scalar[float]):
    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *constraints: Constraint[float],
        optional: bool = False,
        secret: bool = False,
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
            secret=secret,
            definition=FloatDefinition(
                *constraints,
                *literal_constraint,
                minimum=minimum,
                maximum=maximum,
            ),
            default=default,
        )
