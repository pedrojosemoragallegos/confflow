from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING, Final

from typing_extensions import override

from confflow.core.definitions.date_time import LocalTime as LocalTimeDefinition

from .base import Array

if TYPE_CHECKING:
    from confflow.core.definitions.constraints import Constraint


class LocalTime(Array[time]):
    __slots__ = ("__definition",)

    def __init__(
        self,
        name: str,
        description: str,
        /,
        *constraints: Constraint[time],
        optional: bool = False,
        minimum: time | None = None,
        maximum: time | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[LocalTimeDefinition] = LocalTimeDefinition(
            *constraints, minimum=minimum, maximum=maximum
        )

    @property
    def definition(self) -> LocalTimeDefinition:
        return self.__definition

    @override
    def _validate_item(self, value: time, /) -> None:
        self.__definition.validate(value)
