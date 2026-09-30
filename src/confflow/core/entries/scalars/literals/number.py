from __future__ import annotations

from ....definitions.literals import NumberLiteral as NumberLiteralDefinition
from .base import Literal


class NumberLiteral(Literal[int]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *values: int,
        optional: bool = False,
        default: int | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=NumberLiteralDefinition(*values),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
