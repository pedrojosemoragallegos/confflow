from __future__ import annotations

from datetime import datetime

from typing_extensions import override

from .base import Field


class OffsetDateTime(Field[datetime]):
    @override
    def _typecheck(self, value: object, /) -> bool:
        return (
            type(value) is datetime
            and value.tzinfo is not None
            and value.utcoffset() is not None
        )
