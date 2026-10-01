from __future__ import annotations

from confflow.core.definitions import Integer as IntegerDefinition

from .base import Scalar


class Integer(Scalar[int]):
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
            definition=IntegerDefinition(minimum=minimum, maximum=maximum),
            default=default,
        )
