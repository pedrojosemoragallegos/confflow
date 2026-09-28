from __future__ import annotations

from typing import TYPE_CHECKING, Final, final

from typing_extensions import override

from ..exceptions import SchemaError, ValidationError
from ._validation import _present_count, _validate_group_members
from .base import Rule

if TYPE_CHECKING:
    from collections.abc import Collection

    from ..members.base import Entry


@final
class ExactlyOneOf(Rule):
    __slots__ = ("__members",)

    def __init__(self, *members: Entry) -> None:
        member_tuple = _validate_group_members(members)
        if sum(member.required for member in member_tuple) > 1:
            raise SchemaError(
                "exactly-one rule cannot contain more than one required member"
            )
        self.__members: Final[tuple[Entry, ...]] = member_tuple

    @property
    @override
    def members(self) -> tuple[Entry, ...]:
        return self.__members

    @override
    def validate(
        self, present_members: Collection[Entry], path: tuple[str | int, ...]
    ) -> None:
        if _present_count(self.__members, present_members) != 1:
            raise ValidationError("exactly one member must be present", path)

    @override
    def __repr__(self) -> str:
        return f"ExactlyOneOf(members={self.__members!r})"
