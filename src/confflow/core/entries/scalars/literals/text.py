from __future__ import annotations

from ....definitions.literals import TextLiteral as TextLiteralDefinition
from .base import Literal


class TextLiteral(Literal[str]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *values: str,
        optional: bool = False,
        default: str | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=TextLiteralDefinition(*values),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
