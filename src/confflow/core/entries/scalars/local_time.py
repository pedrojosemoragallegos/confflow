from __future__ import annotations

from datetime import time

from ...definitions.local_time import LocalTime as LocalTimeDefinition
from .base import Scalar


class LocalTime(Scalar[time]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: time | None = None,
        minimum: time | None = None,
        maximum: time | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=LocalTimeDefinition(minimum=minimum, maximum=maximum),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
