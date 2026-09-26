from __future__ import annotations

from typing_extensions import override

from .base import Field


class Boolean(Field[bool]):
    __slots__ = ()

    @override
    def _typecheck(self, value: object, /) -> bool:
        return type(value) is bool
