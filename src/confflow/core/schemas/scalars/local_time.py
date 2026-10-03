from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING, final

from confflow.core.definitions import LocalTime as LocalTimeDefinition
from confflow.core.definitions.constraints.literal import Literal

from .base import Scalar

if TYPE_CHECKING:
    from collections.abc import Sequence

    from confflow.core.definitions.constraints import Constraint


@final
class LocalTime(Scalar[time]):
    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *constraints: Constraint[time],
        optional: bool = False,
        secret: bool = False,
        default: time | None = None,
        minimum: time | None = None,
        maximum: time | None = None,
        literal: Sequence[time] | None = None,
    ) -> None:
        literal_constraint: tuple[()] | tuple[Literal[time]] = (
            () if literal is None else (Literal(*literal),)
        )

        super().__init__(
            name,
            description,
            optional=optional,
            secret=secret,
            definition=LocalTimeDefinition(
                *constraints, *literal_constraint, minimum=minimum, maximum=maximum
            ),
            default=default,
        )
