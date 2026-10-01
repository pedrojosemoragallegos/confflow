from __future__ import annotations

from typing import ClassVar

from typing_extensions import override

from .base import Definition
from .exceptions import DefinitionError


class Boolean(Definition[bool]):
    __slots__ = ()

    VALUE_TYPE: ClassVar[type[bool]] = bool

    @override
    def validate(self, value: object, /) -> None:
        if type(value) is not bool:
            raise DefinitionError("expected a boolean")

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}()"
