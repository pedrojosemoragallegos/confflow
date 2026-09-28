from __future__ import annotations

from typing import ClassVar

from .literal import Literal


class TextLiteral(Literal[str]):
    __slots__ = ()

    _EXPECTED_TYPE: ClassVar[type[object] | None] = str
