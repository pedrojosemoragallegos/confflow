from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, final

from confflow.core.definitions import LocalDateTime as LocalDateTimeDefinition
from confflow.core.definitions.constraints.literal import Literal

from .base import Scalar

if TYPE_CHECKING:
    from collections.abc import Sequence

    from confflow.core.definitions.constraints import Constraint


@final
class LocalDateTime(Scalar[datetime]):
    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *constraints: Constraint[datetime],
        optional: bool = False,
        secret: bool = False,
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
            secret=secret,
            definition=LocalDateTimeDefinition(
                *constraints, *literal_constraint, minimum=minimum, maximum=maximum
            ),
            default=default,
        )
