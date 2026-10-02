from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Final

from typing_extensions import override

from confflow.core.definitions.date_time import LocalDateTime as LocalDateTimeDefinition

from .base import Array

if TYPE_CHECKING:
    from confflow.core.definitions.constraints import Constraint


class LocalDateTime(Array[datetime]):
    __slots__ = ("__definition",)

    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *constraints: Constraint[datetime],
        optional: bool = False,
        minimum: datetime | None = None,
        maximum: datetime | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[LocalDateTimeDefinition] = LocalDateTimeDefinition(
            *constraints, minimum=minimum, maximum=maximum
        )

    @property
    def definition(self) -> LocalDateTimeDefinition:
        return self.__definition

    @override
    def _validate_item(self, value: datetime, /) -> None:
        self.__definition.validate(value)
