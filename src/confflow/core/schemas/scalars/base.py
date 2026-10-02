from __future__ import annotations

from typing import TYPE_CHECKING, Final, Generic, TypeVar

from typing_extensions import override

from confflow.core.errors import ValidationError
from confflow.core.schemas.base import Schema
from confflow.core.types import Value

if TYPE_CHECKING:
    from confflow.core.definitions import Definition

ValueT = TypeVar(name="ValueT", bound=Value)


class Scalar(Schema[ValueT], Generic[ValueT]):
    __slots__ = ("__default", "__definition")

    def __init__(
        self,
        name: str,
        description: str,
        /,
        *,
        optional: bool,
        definition: Definition[ValueT],
        default: ValueT | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        if default is not None:
            try:
                definition.validate(default)
            except ValidationError as error:
                error.prepend_path(name)
                raise

        self.__definition: Final[Definition[ValueT]] = definition
        self.__default: Final[ValueT | None] = default

    @property
    def definition(self) -> Definition[ValueT]:
        return self.__definition

    @property
    def default(self) -> ValueT | None:
        return self.__default

    @override
    def validate(self, value: ValueT, /) -> None:
        self.__definition.validate(value)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"definition={self.__definition!r}, "
            f"default={self.__default!r})"
        )
