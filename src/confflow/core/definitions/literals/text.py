from __future__ import annotations

from typing import ClassVar

from .base import Literal


class TextLiteral(Literal[str]):
    __slots__ = ()

    VALUE_TYPE: ClassVar[type[str]] = str
