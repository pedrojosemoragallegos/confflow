from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import override

from confflow.core.definitions.string import String as StringDefinition

from .base import Array

if TYPE_CHECKING:
    from confflow.core.definitions.constraints import Constraint


class String(Array[str]):
    __slots__ = ("__definition",)

    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *constraints: Constraint[str],
        optional: bool = False,
        minimum: int | None = None,
        maximum: int | None = None,
        pattern: str | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[StringDefinition] = StringDefinition(
            *constraints, minimum=minimum, maximum=maximum, pattern=pattern
        )

    @property
    def definition(self) -> StringDefinition:
        return self.__definition

    @override
    def _validate_item(self, value: str, /) -> None:
        self.__definition.validate(value)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"definition={self.__definition!r})"
        )
