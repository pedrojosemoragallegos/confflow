from __future__ import annotations

from datetime import time

from typing_extensions import override

from .base import Field


class Time(Field[time]):
    @override
    def _typecheck(self, value: object, /) -> bool:
        return type(value) is time and value.tzinfo is None
