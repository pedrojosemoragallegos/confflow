from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Final

from typing_extensions import override

from confflow.core.schemas.base import Schema

if TYPE_CHECKING:
    from confflow.core.constraints.table import Constraint


class Table(Schema[Mapping[str, object]]):
    __slots__ = ("__constraints", "__schemas")

    def __init__(
        self,
        name: str,
        description: str,
        /,
        *schemas: Schema[Any],
        optional: bool = False,
        constraints: Sequence[Constraint] | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        names: set[str] = set()

        for schema in schemas:
            if schema.name in names:
                raise ValueError(f"duplicate table schema name {schema.name!r}")

            names.add(schema.name)

        self.__schemas: Final[tuple[Schema[Any], ...]] = schemas
        self.__constraints: Final[tuple[Constraint, ...]] = (
            tuple(constraints) if constraints is not None else ()
        )

    @property
    def schemas(self) -> tuple[Schema[Any], ...]:
        return self.__schemas

    @property
    def constraints(self) -> tuple[Constraint, ...]:
        return self.__constraints

    @override
    def validate(self, value: Mapping[str, object], /) -> None:
        for schema in self.__schemas:
            if schema.name not in value:
                if schema.optional:
                    continue

                raise ValueError(f"required table entry {schema.name!r} is missing")

            schema.validate(value[schema.name])

        for constraint in self.__constraints:
            constraint(value)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"schemas={self.__schemas!r}, "
            f"constraints={self.__constraints!r})"
        )
