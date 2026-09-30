from __future__ import annotations

from ...definitions.text import Text as TextDefinition
from .base import Scalar


class Text(Scalar[str]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: str | None = None,
        minimum: int | None = None,
        maximum: int | None = None,
        length: int | None = None,
        pattern: str | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=TextDefinition(
                minimum=minimum,
                maximum=maximum,
                length=length,
                pattern=pattern,
            ),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
