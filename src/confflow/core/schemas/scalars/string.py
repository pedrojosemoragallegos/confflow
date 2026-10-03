from __future__ import annotations

from typing import TYPE_CHECKING, final

from confflow.core.definitions.constraints.literal import Literal
from confflow.core.definitions.string import String as StringDefinition
from confflow.core.schemas.scalars.base import Scalar

if TYPE_CHECKING:
    from collections.abc import Sequence

    from confflow.core.definitions.constraints import Constraint


@final
class String(Scalar[str]):
    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *constraints: Constraint[str],
        optional: bool = False,
        secret: bool = False,
        default: str | None = None,
        minimum: int | None = None,
        maximum: int | None = None,
        pattern: str | None = None,
        literal: Sequence[str] | None = None,
    ) -> None:
        literal_constraint: tuple[()] | tuple[Literal[str]] = (
            () if literal is None else (Literal(*literal),)
        )

        super().__init__(
            name,
            description,
            optional=optional,
            secret=secret,
            default=default,
            definition=StringDefinition(
                *constraints,
                *literal_constraint,
                minimum=minimum,
                maximum=maximum,
                pattern=pattern,
            ),
        )
