from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from typing_extensions import override

from confflow.core.errors import (
    SchemaError,
    ValidationError,
    constraint_name,
    constraint_rule,
)
from confflow.core.schemas.base import Schema
from confflow.core.schemas.table.constraints import Constraint


class Table(Schema[Mapping[str, object]]):
    __slots__ = ("__constraints", "__schema_names", "__schemas")

    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *items: Schema[Any] | Constraint,
        optional: bool = False,
    ) -> None:
        super().__init__(name, description, optional=optional)

        names: set[str] = set()
        schemas: list[Schema[Any]] = []
        constraints: list[Constraint] = []

        for item in items:
            if isinstance(item, Schema):
                if constraints:
                    raise SchemaError("table schemas must precede table constraints")
                if item.name in names:
                    raise SchemaError(f"duplicate table schema name {item.name!r}")
                names.add(item.name)
                schemas.append(item)
            elif isinstance(item, Constraint):
                constraints.append(item)
            else:
                raise SchemaError("table items must be schemas or table constraints")

        table_constraints = tuple(constraints)

        for constraint in table_constraints:
            if any(not isinstance(field, str) for field in constraint.fields):
                raise SchemaError("table constraint operands must be child names")

            if len(set(constraint.fields)) != len(constraint.fields):
                raise SchemaError(
                    f"constraint {constraint_name(constraint)!r} contains duplicate "
                    "field references"
                )

            missing: tuple[str, ...] = tuple(
                field for field in constraint.fields if field not in names
            )

            if missing:
                raise SchemaError(
                    f"constraint {constraint_name(constraint)!r} references "
                    "unknown table fields "
                    f"{missing!r}"
                )

        self.__schemas: Final[tuple[Schema[Any], ...]] = tuple(schemas)
        self.__schema_names: Final[frozenset[str]] = frozenset(names)
        self.__constraints: Final[tuple[Constraint, ...]] = table_constraints

    @property
    def schemas(self) -> tuple[Schema[Any], ...]:
        return self.__schemas

    @property
    def constraints(self) -> tuple[Constraint, ...]:
        return self.__constraints

    @override
    def validate(self, value: Mapping[str, object], /) -> None:
        unknown: tuple[str, ...] = tuple(
            name for name in value if name not in self.__schema_names
        )

        if unknown:
            name = unknown[0]
            raise ValidationError(
                f"unexpected table entry; other unknown entries: {unknown[1:]!r}",
                path=(name,),
                value=value[name],
                expected="declared table field",
            )

        for schema in self.__schemas:
            if schema.name not in value:
                if schema.optional:
                    continue

                raise ValidationError(
                    "required table entry is missing",
                    path=(schema.name,),
                    expected="required field",
                )

            try:
                schema.validate(value[schema.name])
            except ValidationError as error:
                error.prepend_path(schema.name)
                raise
            except (TypeError, ValueError, RuntimeError) as error:
                raise ValidationError(
                    str(error),
                    path=(schema.name,),
                    value=value[schema.name],
                    expected=type(schema).__name__,
                ) from error

        for constraint in self.__constraints:
            try:
                constraint(value)
            except ValidationError:
                raise
            except (TypeError, ValueError, RuntimeError) as error:
                constraint_value: dict[str, object] = {
                    name: value[name] for name in constraint.fields if name in value
                }
                raise ValidationError(
                    str(error),
                    value=constraint_value,
                    constraint=constraint_name(constraint),
                    expected=constraint_rule(constraint),
                ) from error

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
