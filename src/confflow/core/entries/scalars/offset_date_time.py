from __future__ import annotations

from datetime import datetime

from ...definitions.offset_date_time import OffsetDateTime as OffsetDateTimeDefinition
from .base import Scalar


class OffsetDateTime(Scalar[datetime]):
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
            definition=OffsetDateTimeDefinition(minimum=minimum, maximum=maximum),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
