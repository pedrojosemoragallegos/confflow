from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, final

from confflow.core.definitions import LocalDate as LocalDateDefinition
from confflow.core.definitions.constraints.literal import Literal

from .base import Scalar

if TYPE_CHECKING:
    from collections.abc import Sequence

    from confflow.core.definitions.constraints import Constraint


@final
class LocalDate(Scalar[date]):
    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *constraints: Constraint[date],
        optional: bool = False,
        secret: bool = False,
        default: date | None = None,
        minimum: date | None = None,
        maximum: date | None = None,
        literal: Sequence[date] | None = None,
    ) -> None:
        literal_constraint: tuple[()] | tuple[Literal[date]] = (
            () if literal is None else (Literal(*literal),)
        )

        super().__init__(
            name,
            description,
            optional=optional,
            secret=secret,
            definition=LocalDateDefinition(
                *constraints, *literal_constraint, minimum=minimum, maximum=maximum
            ),
            default=default,
        )
