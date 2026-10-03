from __future__ import annotations

from typing import final

from typing_extensions import override

from .base import Definition


@final
class Boolean(Definition[bool]):
    __slots__ = ()

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}()"
