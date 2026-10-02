from __future__ import annotations

from json import dumps
from typing import TYPE_CHECKING, Any

from .base import Comparision

if TYPE_CHECKING:
    from collections.abc import Mapping


class LessThanOrEqual(Comparision):
    __slots__ = ()

    def __call__(self, value: Mapping[str, Any], /) -> None:
        if self.left not in value or self.right not in value:
            return
        try:
            valid = value[self.left] <= value[self.right]
        except TypeError as error:
            raise ValueError(
                f"fields {self.left!r} and {self.right!r} cannot be compared"
            ) from error
        if not valid:
            raise ValueError(f"field {self.left!r} must be <= field {self.right!r}")

    def __str__(self) -> str:
        return f"{dumps(self.left)} must be <= {dumps(self.right)}"
