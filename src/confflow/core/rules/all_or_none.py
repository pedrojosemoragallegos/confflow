from __future__ import annotations

from typing import TYPE_CHECKING, Final, final

from typing_extensions import override

from ..exceptions import ValidationError
from ._validation import _present_count, _validate_group_members
from .base import Rule

if TYPE_CHECKING:
    from collections.abc import Collection

    from ..members.base import Entry


@final
class AllOrNone(Rule):
    __slots__ = ("__members",)

    def __init__(self, *members: Entry) -> None:
        self.__members: Final[tuple[Entry, ...]] = _validate_group_members(members)

    @property
    @override
    def members(self) -> tuple[Entry, ...]:
        return self.__members

    @override
    def validate(
        self, present_members: Collection[Entry], path: tuple[str | int, ...]
    ) -> None:
        count = _present_count(self.__members, present_members)
        if count not in (0, len(self.__members)):
            raise ValidationError(
                "either all members or none of them must be present", path
            )

    @override
    def __repr__(self) -> str:
        return f"AllOrNone(members={self.__members!r})"
