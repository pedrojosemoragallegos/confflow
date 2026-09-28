from __future__ import annotations

from typing import ClassVar

from .literal import Literal


class BooleanLiteral(Literal[bool]):
    __slots__ = ()

    _EXPECTED_TYPE: ClassVar[type[object] | None] = bool
