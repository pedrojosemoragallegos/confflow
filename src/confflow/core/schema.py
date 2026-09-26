from __future__ import annotations

import operator
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Self

from confflow.core.constraint import Constraint, _Constraint
from confflow.core.fields import (
    Array,
    ArrayOfTables,
    Boolean,
    Date,
    Field,
    Float,
    Integer,
    Literal,
    LocalDateTime,
    OffsetDateTime,
    String,
    Time,
    _Table,
)
from confflow.core.render import atomic_write, template_lines
from confflow.core.shared import (
    ConfigurationError,
    S,
    T_co,
    TOMLValue,
    V,
    validate_name,
)
from confflow.core.validate import prepare

if TYPE_CHECKING:
    import os
    from collections.abc import Mapping
    from datetime import date, datetime, time

_ORDERABLE = (String, Integer, Float, Date, Time, LocalDateTime, OffsetDateTime)

_COMPARISON_OPERATORS = {
    "Equal": operator.eq,
    "NotEqual": operator.ne,
    "LessThan": operator.lt,
    "LessThanOrEqual": operator.le,
    "GreaterThan": operator.gt,
    "GreaterThanOrEqual": operator.ge,
}


class Schema:
    def __init__(self, name: str, description: str, /) -> None:
        validate_name(name)

        self._name: str = name
        self._description = description
        self._fields: dict[str, Field[TOMLValue]] = {}
        self._constraints: list[Constraint] = []
        self._items: list[Field[TOMLValue] | Constraint] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def _register(self, field: Field[T_co], /, *, record: bool = True) -> Field[T_co]:
        if (existing := self._fields.get(field.name)) is not None:
            if existing is field:
                return field
            msg = f"duplicate field name: {field.name}"
            raise ValueError(msg)
        if isinstance(field, _Table) and field.schema is self:
            msg = "a schema cannot contain itself"
            raise ValueError(msg)
        self._fields[field.name] = field
        if record:
            self._items.append(field)
        return field

    def add(self, *fields: Field[TOMLValue]) -> Self:
        for field in fields:
            if not isinstance(field, Field):
                msg = f"cannot add {type(field).__name__}"
                raise TypeError(msg)

            self._register(field)

        return self

    def _add_constraint(self, constraint: Constraint, /) -> Self:
        for target in constraint.targets:
            if isinstance(target, Schema):
                nested: Field[TOMLValue] | None = self._fields.get(target.name)

                if not isinstance(nested, _Table) or nested.schema is not target:
                    msg = f"schema {target.name!r} is not a child of {self.name!r}"
                    raise ValueError(msg)
            else:
                self._register(target, record=False)

        self._constraints.append(constraint)
        self._items.append(constraint)

        return self

    def Schema(self, name: str, description: str, /, *, required: bool = False) -> Self:
        schema: Self = type(self)(name, description)

        self._register(_Table(schema, required=required))

        return schema

    def String(
        self,
        name: str,
        description: str,
        /,
        *,
        required: bool = False,
        default: str | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        pattern: str | None = None,
    ) -> Self:
        return self.add(
            String(
                name,
                description,
                required=required,
                default=default,
                min_length=min_length,
                max_length=max_length,
                pattern=pattern,
            ),
        )

    def Literal(
        self,
        name: str,
        description: str,
        /,
        *values: S,
        required: bool = False,
        default: S | None = None,
    ) -> Self:
        return self.add(
            Literal(
                name,
                description,
                *values,
                required=required,
                default=default,
            ),
        )

    def Integer(
        self,
        name: str,
        description: str,
        /,
        *,
        required: bool = False,
        default: int | None = None,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> Self:
        return self.add(
            Integer(
                name,
                description,
                required=required,
                default=default,
                minimum=minimum,
                maximum=maximum,
            ),
        )

    def Float(
        self,
        name: str,
        description: str,
        /,
        *,
        required: bool = False,
        default: float | None = None,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> Self:
        return self.add(
            Float(
                name,
                description,
                required=required,
                default=default,
                minimum=minimum,
                maximum=maximum,
            ),
        )

    def Boolean(
        self,
        name: str,
        description: str,
        /,
        *,
        required: bool = False,
        default: bool | None = None,
    ) -> Self:
        return self.add(Boolean(name, description, required=required, default=default))

    def Date(
        self,
        name: str,
        description: str,
        /,
        *,
        required: bool = False,
        default: date | None = None,
    ) -> Self:
        return self.add(Date(name, description, required=required, default=default))

    def Time(
        self,
        name: str,
        description: str,
        /,
        *,
        required: bool = False,
        default: time | None = None,
    ) -> Self:
        return self.add(Time(name, description, required=required, default=default))

    def LocalDateTime(
        self,
        name: str,
        description: str,
        /,
        *,
        required: bool = False,
        default: datetime | None = None,
    ) -> Self:
        return self.add(
            LocalDateTime(name, description, required=required, default=default),
        )

    def OffsetDateTime(
        self,
        name: str,
        description: str,
        /,
        *,
        required: bool = False,
        default: datetime | None = None,
    ) -> Self:
        return self.add(
            OffsetDateTime(name, description, required=required, default=default),
        )

    def Array(
        self,
        name: str,
        description: str,
        /,
        *,
        element: Field[V],
        required: bool = False,
        default: list[V] | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> Self:
        return self.add(
            Array(
                name,
                description,
                element=element,
                required=required,
                default=default,
                min_length=min_length,
                max_length=max_length,
            ),
        )

    def ArrayOfTables(
        self,
        name: str,
        description: str,
        schema: _AnySchema,
        /,
        *,
        required: bool = False,
        default: list[dict[str, TOMLValue]] | None = None,
    ) -> Self:
        return self.add(
            ArrayOfTables(
                name,
                description,
                schema,
                required=required,
                default=default,
            ),
        )

    def _presence(
        self,
        name: str,
        targets: tuple[Field[TOMLValue] | _AnySchema, ...],
        /,
    ) -> Self:
        def check(_: Mapping[str, TOMLValue], present: frozenset[str]) -> bool:
            count = sum(target.name in present for target in targets)
            if name == "Exclusive":
                return count <= 1
            if name == "ExactlyOne":
                return count == 1
            if name == "AtLeastOne":
                return count >= 1
            return count in (0, len(targets))

        return self._add_constraint(_Constraint(name, targets, check))

    def Exclusive(self, *targets: Field[TOMLValue] | _AnySchema) -> Self:
        return self._presence("Exclusive", targets)

    def ExactlyOne(self, *targets: Field[TOMLValue] | _AnySchema) -> Self:
        return self._presence("ExactlyOne", targets)

    def AtLeastOne(self, *targets: Field[TOMLValue] | _AnySchema) -> Self:
        return self._presence("AtLeastOne", targets)

    def AllOrNone(self, *targets: Field[TOMLValue] | _AnySchema) -> Self:
        return self._presence("AllOrNone", targets)

    def Requires(
        self,
        source: Field[TOMLValue] | _AnySchema,
        requirement: Field[TOMLValue] | _AnySchema,
        /,
    ) -> Self:
        return self._add_constraint(
            _Constraint(
                "Requires",
                (source, requirement),
                lambda _, present: source.name not in present
                or requirement.name in present,
            ),
        )

    def _comparison(self, name: str, a: Field[T_co], b: Field[T_co], /) -> Self:
        if type(a) is not type(b):
            msg = "compared fields must have the same field type"
            raise TypeError(msg)
        if name not in ("Equal", "NotEqual") and not isinstance(a, _ORDERABLE):
            msg = "these fields do not support ordering"
            raise TypeError(msg)

        def check(values: Mapping[str, TOMLValue], _: frozenset[str]) -> bool:
            if a.name not in values or b.name not in values:
                return True
            return _COMPARISON_OPERATORS[name](
                values[a.name],  # ty: ignore[invalid-argument-type]
                values[b.name],  # ty: ignore[invalid-argument-type]
            )

        return self._add_constraint(_Constraint(name, (a, b), check))

    def Equal(self, a: Field[T_co], b: Field[T_co], /) -> Self:
        return self._comparison("Equal", a, b)

    def NotEqual(self, a: Field[T_co], b: Field[T_co], /) -> Self:
        return self._comparison("NotEqual", a, b)

    def LessThan(self, a: Field[T_co], b: Field[T_co], /) -> Self:
        return self._comparison("LessThan", a, b)

    def LessThanOrEqual(self, a: Field[T_co], b: Field[T_co], /) -> Self:
        return self._comparison("LessThanOrEqual", a, b)

    def GreaterThan(self, a: Field[T_co], b: Field[T_co], /) -> Self:
        return self._comparison("GreaterThan", a, b)

    def GreaterThanOrEqual(self, a: Field[T_co], b: Field[T_co], /) -> Self:
        return self._comparison("GreaterThanOrEqual", a, b)

    def _prepare(
        self,
        source: Mapping[str, object],
        path: str,
        /,
    ) -> dict[str, TOMLValue]:
        return prepare(self, source, path)

    def validate(self, config: Mapping[str, object], /) -> dict[str, TOMLValue]:
        return self._prepare(config, self.name or "")

    def load(self, path: str | os.PathLike[str], /) -> dict[str, TOMLValue]:
        try:
            with Path(path).open("rb") as stream:
                raw = tomllib.load(stream)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ConfigurationError(str(path), str(exc)) from exc
        return self._prepare(raw, self.name)

    def template(
        self,
        path: str | Path,
        /,
        *,
        overwrite: bool = False,
        parents: bool = True,
    ) -> None:
        target = Path(path)
        if target.exists() and not overwrite:
            raise FileExistsError(target)
        if not target.parent.exists():
            if parents:
                target.parent.mkdir(parents=True, exist_ok=True)
            else:
                raise FileNotFoundError(target.parent)

        content = "\n".join(template_lines(self, top=True)) + "\n"
        atomic_write(target, content, parents=False)


# Alias for `Schema` type hints; the class also defines a method named `Schema`,
# which shadows the class name within its own body.
_AnySchema = Schema
