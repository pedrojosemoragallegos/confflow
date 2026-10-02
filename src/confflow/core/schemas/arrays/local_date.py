from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Final

from typing_extensions import override

from confflow.core.definitions.date_time import LocalDate as LocalDateDefinition

from .base import Array

if TYPE_CHECKING:
    from confflow.core.definitions.constraints import Constraint


class LocalDate(Array[date]):
    __slots__ = ("__definition",)

    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *constraints: Constraint[date],
        optional: bool = False,
        minimum: date | None = None,
        maximum: date | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[LocalDateDefinition] = LocalDateDefinition(
            *constraints, minimum=minimum, maximum=maximum
        )

    @property
    def definition(self) -> LocalDateDefinition:
        return self.__definition

    @override
    def _validate_item(self, value: date, /) -> None:
        self.__definition.validate(value)
