from __future__ import annotations

from ...definitions.boolean import Boolean as BooleanDefinition
from .base import Scalar


class Boolean(Scalar[bool]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: bool | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=BooleanDefinition(),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
