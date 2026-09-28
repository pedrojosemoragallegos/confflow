from __future__ import annotations

from typing import Final, final

from typing_extensions import override

from ..exceptions import SchemaError
from ..schema import Schema
from .base import Entry


@final
class Section(Entry):
    __slots__ = ("__schema",)

    @override
    def __init__(  # ty: ignore[invalid-method-override]
        self,
        name: str,
        description: str = "",
        /,
        *,
        required: bool = False,
        schema: Schema,
    ) -> None:
        super().__init__(name, description, required=required)
        if not isinstance(schema, Schema):
            raise SchemaError("section schema must be a Schema")
        self.__schema: Final[Schema] = schema

    @property
    def schema(self) -> Schema:
        return self.__schema

    @override
    def __repr__(self) -> str:
        return (
            f"Section(name={self.name!r}, description={self.description!r}, "
            f"required={self.required!r}, schema={self.__schema!r})"
        )
