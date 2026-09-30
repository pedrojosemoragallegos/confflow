from __future__ import annotations

from datetime import datetime

from ....definitions.literals import (
    LocalDateTimeLiteral as LocalDateTimeLiteralDefinition,
)
from .base import Literal


class LocalDateTimeLiteral(Literal[datetime]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *values: datetime,
        optional: bool = False,
        default: datetime | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=LocalDateTimeLiteralDefinition(*values),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
