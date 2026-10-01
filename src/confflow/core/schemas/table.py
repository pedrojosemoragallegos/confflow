from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from typing_extensions import override

from confflow.core.schemas.base import Schema


class Table(Schema[Mapping[str, object]]):
    __slots__ = ("__schemas",)

    def __init__(
        self,
        name: str,
        description: str,
        /,
        *schemas: Schema[Any],
        optional: bool = False,
    ) -> None:
        super().__init__(name, description, optional=optional)

        names: set[str] = set()

        for schema in schemas:
            if schema.name in names:
                raise ValueError(f"duplicate table schema name {schema.name!r}")

            names.add(schema.name)

        self.__schemas: Final[tuple[Schema[Any], ...]] = schemas

    @property
    def schemas(self) -> tuple[Schema[Any], ...]:
        return self.__schemas

    @override
    def validate(self, value: Mapping[str, object], /) -> None:
        for schema in self.__schemas:
            if schema.name not in value:
                if schema.optional:
                    continue

                raise ValueError(f"required table entry {schema.name!r} is missing")

            schema.validate(value[schema.name])

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"schemas={self.__schemas!r})"
        )
