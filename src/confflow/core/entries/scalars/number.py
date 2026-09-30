from __future__ import annotations

from ...definitions.number import Number as NumberDefinition
from .base import Scalar


class Number(Scalar[int]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: int | None = None,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=NumberDefinition(minimum=minimum, maximum=maximum),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
