from __future__ import annotations

from confflow.core.definitions import Float as FloatDefinition

from .base import Scalar


class Float(Scalar[float]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: float | None = None,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=FloatDefinition(minimum=minimum, maximum=maximum),
            default=default,
        )
