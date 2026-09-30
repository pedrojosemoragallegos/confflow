from __future__ import annotations

from ....definitions.literals import DecimalLiteral as DecimalLiteralDefinition
from .base import Literal


class DecimalLiteral(Literal[float]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *values: float,
        optional: bool = False,
        default: float | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=DecimalLiteralDefinition(*values),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
