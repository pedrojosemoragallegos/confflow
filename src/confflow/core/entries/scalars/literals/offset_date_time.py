from __future__ import annotations

from datetime import datetime

from ....definitions.literals import (
    OffsetDateTimeLiteral as OffsetDateTimeLiteralDefinition,
)
from .base import Literal


class OffsetDateTimeLiteral(Literal[datetime]):
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
            definition=OffsetDateTimeLiteralDefinition(*values),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
