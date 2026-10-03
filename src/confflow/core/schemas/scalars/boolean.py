from __future__ import annotations

from confflow.core.definitions import Boolean as BooleanDefinition

from .base import Scalar


class Boolean(Scalar[bool]):
    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *,
        optional: bool = False,
        secret: bool = False,
        default: bool | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            secret=secret,
            definition=BooleanDefinition(),
            default=default,
        )
