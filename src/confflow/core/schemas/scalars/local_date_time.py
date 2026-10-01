from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from confflow.core.constraints.literal import Literal
from confflow.core.definitions import LocalDateTime as LocalDateTimeDefinition

from .base import Scalar

if TYPE_CHECKING:
    from collections.abc import Sequence

    from confflow.core.constraints import Constraint


class LocalDateTime(Scalar[datetime]):
    def __init__(
        self,
        name: str,
        description: str,
        /,
        *constraints: Constraint[datetime],
        optional: bool = False,
        default: datetime | None = None,
        minimum: datetime | None = None,
        maximum: datetime | None = None,
        literal: Sequence[datetime] | None = None,
    ) -> None:
        literal_constraint: tuple[()] | tuple[Literal[datetime]] = (
            () if literal is None else (Literal(*literal),)
        )

        super().__init__(
            name,
            description,
            optional=optional,
            definition=LocalDateTimeDefinition(
                *constraints,
                *literal_constraint,
                minimum=minimum,
                maximum=maximum,
            ),
            default=default,
        )
