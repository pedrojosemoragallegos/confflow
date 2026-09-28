from __future__ import annotations

from typing import Final, Generic, TypeVar

from typing_extensions import override

from ..definitions.base import Definition, TomlScalar
from ..exceptions import SchemaError, ValidationError
from .base import Entry

FieldValueT = TypeVar("FieldValueT", bound=TomlScalar)


class Field(Entry, Generic[FieldValueT]):
    __slots__ = ("__default", "__definition")

    @override
    def __init__(  # ty: ignore[invalid-method-override]
        self,
        name: str,
        description: str,
        required: bool,
        definition: Definition[FieldValueT],
        default: FieldValueT | None = None,
    ) -> None:
        super().__init__(name, description, required=required)
        if not isinstance(definition, Definition):
            raise SchemaError("field definition must be a Definition")

        if default is not None:
            try:
                definition.validate(default, ())
            except ValidationError as error:
                raise SchemaError(
                    "field default does not satisfy its definition"
                ) from error

        self.__definition: Final[Definition[FieldValueT]] = definition
        self.__default: Final[FieldValueT | None] = default

    @property
    def definition(self) -> Definition[FieldValueT]:
        return self.__definition

    @property
    def default(self) -> FieldValueT | None:
        return self.__default

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, required={self.required!r}, "
            f"definition={self.__definition!r}, default={self.__default!r})"
        )
