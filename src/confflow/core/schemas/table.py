from __future__ import annotations

from collections.abc import Mapping
from typing import Final

from typing_extensions import override

from confflow.core.schemas.base import Schema
from confflow.core.schemas.exceptions import SchemaError


class Table(Schema):
    __slots__ = ("__schemas",)

    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        schemas: tuple[Schema, ...],
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__schemas: Final[tuple[Schema, ...]] = schemas

    @property
    def schemas(self) -> tuple[Schema, ...]:
        return self.__schemas

    @override
    def validate(self, value: object, /) -> None:
        super().validate(value)

        if not isinstance(value, Mapping):
            raise SchemaError("table value must be a mapping")

        for schema in self.__schemas:
            if schema.name not in value:
                if schema.optional:
                    continue

                raise SchemaError(f"required table entry {schema.name!r} is missing")

            schema.validate(value[schema.name])

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"schemas={self.__schemas!r})"
        )
