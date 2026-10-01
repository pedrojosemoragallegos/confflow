from __future__ import annotations

from typing import Final

from typing_extensions import override

from confflow.core.definitions.string import String as StringDefinition

from .base import Array


class String(Array):
    __slots__ = ("__definition",)

    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        minimum: int | None = None,
        maximum: int | None = None,
        length: int | None = None,
        pattern: str | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[StringDefinition] = StringDefinition(
            minimum=minimum,
            maximum=maximum,
            length=length,
            pattern=pattern,
        )

    @property
    def definition(self) -> StringDefinition:
        return self.__definition

    @override
    def _validate_item(self, value: object, /) -> None:
        self.__definition.validate(value)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"definition={self.__definition!r})"
        )
