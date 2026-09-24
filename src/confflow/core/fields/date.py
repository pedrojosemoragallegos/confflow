from __future__ import annotations

from datetime import date

from typing_extensions import override

from .base import Field


class Date(Field[date]):
    @override
    def _typecheck(self, value: object, /) -> bool:
        return type(value) is date
