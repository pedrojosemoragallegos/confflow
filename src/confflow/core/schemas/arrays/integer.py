from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import override

from confflow.core.definitions import Integer as IntegerDefinition

from .base import Array

if TYPE_CHECKING:
    from confflow.core.constraints import Constraint


class Integer(Array[int]):
    __slots__ = ("__definition",)

    def __init__(
        self,
        name: str,
        description: str,
        /,
        *constraints: Constraint[int],
        optional: bool = False,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[IntegerDefinition] = IntegerDefinition(
            *constraints, minimum=minimum, maximum=maximum
        )

    @property
    def definition(self) -> IntegerDefinition:
        return self.__definition

    @override
    def _validate_item(self, value: int, /) -> None:
        self.__definition.validate(value)
