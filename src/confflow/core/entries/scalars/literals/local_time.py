from __future__ import annotations

from datetime import time

from ....definitions.literals import LocalTimeLiteral as LocalTimeLiteralDefinition
from .base import Literal


class LocalTimeLiteral(Literal[time]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *values: time,
        optional: bool = False,
        default: time | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=LocalTimeLiteralDefinition(*values),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
