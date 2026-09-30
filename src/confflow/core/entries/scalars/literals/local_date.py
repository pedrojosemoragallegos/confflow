from __future__ import annotations

from datetime import date

from ....definitions.literals import LocalDateLiteral as LocalDateLiteralDefinition
from .base import Literal


class LocalDateLiteral(Literal[date]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *values: date,
        optional: bool = False,
        default: date | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=LocalDateLiteralDefinition(*values),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
