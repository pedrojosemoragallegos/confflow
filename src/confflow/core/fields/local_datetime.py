from __future__ import annotations

from datetime import datetime

from typing_extensions import override

from .base import Field


class LocalDateTime(Field[datetime]):
    __slots__ = ()

    @override
    def _typecheck(self, value: object, /) -> bool:
        return type(value) is datetime and value.tzinfo is None
