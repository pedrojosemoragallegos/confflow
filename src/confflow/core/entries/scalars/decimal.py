from __future__ import annotations

from ...definitions.decimal import Decimal as DecimalDefinition
from .base import Scalar


class Decimal(Scalar[float]):
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
            definition=DecimalDefinition(minimum=minimum, maximum=maximum),
            default=default,
        )

    def _validate(self, value: object) -> None: ...
