from __future__ import annotations

from datetime import datetime

from ...definitions.local_date_time import LocalDateTime as LocalDateTimeDefinition
from .base import Scalar


class LocalDateTime(Scalar[datetime]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: datetime | None = None,
        minimum: datetime | None = None,
        maximum: datetime | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=LocalDateTimeDefinition(minimum=minimum, maximum=maximum),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
