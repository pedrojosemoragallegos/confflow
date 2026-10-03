from __future__ import annotations

from typing import TYPE_CHECKING, final

from confflow.core.definitions import Integer as IntegerDefinition
from confflow.core.definitions.constraints.literal import Literal

from .base import Scalar

if TYPE_CHECKING:
    from collections.abc import Sequence

    from confflow.core.definitions.constraints import Constraint


@final
class Integer(Scalar[int]):
    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *constraints: Constraint[int],
        optional: bool = False,
        secret: bool = False,
        default: int | None = None,
        minimum: int | None = None,
        maximum: int | None = None,
        literal: Sequence[int] | None = None,
    ) -> None:
        literal_constraint: tuple[()] | tuple[Literal[int]] = (
            () if literal is None else (Literal(*literal),)
        )

        super().__init__(
            name,
            description,
            optional=optional,
            secret=secret,
            definition=IntegerDefinition(
                *constraints, *literal_constraint, minimum=minimum, maximum=maximum
            ),
            default=default,
        )
