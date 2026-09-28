from __future__ import annotations

from typing import TYPE_CHECKING, Final, final

from typing_extensions import override

from ..exceptions import ValidationError
from ._validation import _validate_directional_group
from .base import Rule

if TYPE_CHECKING:
    from collections.abc import Collection

    from ..members.base import Entry


@final
class RequiresAll(Rule):
    __slots__ = ("__source", "__targets")

    def __init__(self, source: Entry, *targets: Entry) -> None:
        target_tuple = _validate_directional_group(source, targets)
        self.__source: Final[Entry] = source
        self.__targets: Final[tuple[Entry, ...]] = target_tuple

    @property
    def source(self) -> Entry:
        return self.__source

    @property
    def targets(self) -> tuple[Entry, ...]:
        return self.__targets

    @property
    @override
    def members(self) -> tuple[Entry, ...]:
        return self.__source, *self.__targets

    @override
    def validate(
        self, present_members: Collection[Entry], path: tuple[str | int, ...]
    ) -> None:
        if self.__source in present_members and any(
            target not in present_members for target in self.__targets
        ):
            raise ValidationError(
                f"{self.__source.name!r} requires all target members", path
            )

    @override
    def __repr__(self) -> str:
        return f"RequiresAll(source={self.__source!r}, targets={self.__targets!r})"
