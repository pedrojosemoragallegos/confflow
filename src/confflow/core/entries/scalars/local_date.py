from __future__ import annotations

from datetime import date

from ...definitions.local_date import LocalDate as LocalDateDefinition
from .base import Scalar


class LocalDate(Scalar[date]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: date | None = None,
        minimum: date | None = None,
        maximum: date | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=LocalDateDefinition(minimum=minimum, maximum=maximum),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
