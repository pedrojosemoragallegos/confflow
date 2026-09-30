from __future__ import annotations

from typing import TYPE_CHECKING, Final, final

from typing_extensions import override

from ..exceptions import ValidationError
from ._validation import _validate_pair
from .base import Rule

if TYPE_CHECKING:
    from collections.abc import Collection

    from ..entries.base import Entry


@final
class Requires(Rule):
    __slots__ = ("__source", "__target")

    def __init__(self, *, source: Entry, target: Entry) -> None:
        _validate_pair(source, target)
        self.__source: Final[Entry] = source
        self.__target: Final[Entry] = target

    @property
    def source(self) -> Entry:
        return self.__source

    @property
    def target(self) -> Entry:
        return self.__target

    @property
    @override
    def members(self) -> tuple[Entry, ...]:
        return self.__source, self.__target

    @override
    def validate(
        self, present_members: Collection[Entry], path: tuple[str | int, ...]
    ) -> None:
        if self.__source in present_members and self.__target not in present_members:
            raise ValidationError(
                f"{self.__source.name!r} requires {self.__target.name!r}", path
            )

    @override
    def __repr__(self) -> str:
        return f"Requires(source={self.__source!r}, target={self.__target!r})"
