from __future__ import annotations

import copy
import inspect
import operator
import os
import tempfile
import textwrap
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Self, cast

import tomlkit

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
from confflow.core.shared import (
    ConfigurationError,
    S,
    T_co,
    TOMLValue,
    V,
    validate_name,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import date, datetime, time

_ORDERABLE = (String, Integer, Float, Date, Time, LocalDateTime, OffsetDateTime)

_MISSING = object()


_COMPARISON_OPERATORS = {
    "Equal": operator.eq,
    "NotEqual": operator.ne,
    "LessThan": operator.lt,
    "LessThanOrEqual": operator.le,
    "GreaterThan": operator.gt,
    "GreaterThanOrEqual": operator.ge,
}

_PRESENCE_DESCRIPTIONS = {
    "AllOrNone": (
        "Either all fields in this group must be set, or none of them may be set."
    ),
    "Exclusive": "At most one field in this group may be set.",
    "ExactlyOne": "Exactly one field in this group must be set.",
    "AtLeastOne": "At least one field in this group must be set.",
}

_COMPARISON_DESCRIPTIONS = {
    "Requires": 'If "{0}" is set, "{1}" must also be set.',
    "Equal": '"{0}" and "{1}" must have equal values.',
    "NotEqual": '"{0}" and "{1}" must have different values.',
    "LessThan": '"{0}" must be less than "{1}".',
    "LessThanOrEqual": '"{0}" must be less than or equal to "{1}".',
    "GreaterThan": '"{0}" must be greater than "{1}".',
    "GreaterThanOrEqual": '"{0}" must be greater than or equal to "{1}".',
}


class Schema:
    # -- construction & registration ------------------------------------

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

    # -- field-builder DSL -----------------------------------------------

    def Schema(self, name: str, description: str, /) -> Self:
        schema: Self = type(self)(name, description)

        self._register(_Table(schema))

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

    # -- constraint-builder DSL -------------------------------------------

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

    # -- validation & loading ---------------------------------------------

    def _prepare(
        self,
        source: Mapping[str, object],
        path: str,
        /,
    ) -> dict[str, TOMLValue]:
        for name in source:
            if name not in self._fields:
                unknown_path: str = f"{path}.{name}" if path else name
                raise ConfigurationError(unknown_path, "unknown field")

        present: frozenset[str] = frozenset(source)
        values: dict[str, TOMLValue] = {}

        for name, field in self._fields.items():
            field_path: str = f"{path}.{name}" if path else name
            value: object = self._resolve_source_value(field, name, source, field_path)
            if value is _MISSING:
                continue
            validated: TOMLValue = field.validate(value, field_path)
            values[name] = self._assemble_value(field, field_path, validated)

        for constraint in self._constraints:
            constraint.check(values, present, path)

        return values

    @staticmethod
    def _resolve_source_value(
        field: Field[TOMLValue],
        name: str,
        source: Mapping[str, object],
        field_path: str,
        /,
    ) -> object:
        if name in source:
            return source[name]
        if field.default is not None:
            return copy.deepcopy(field.default)
        if isinstance(field, _Table):
            return _MISSING
        if field.required:
            msg = "required field is missing"
            raise ConfigurationError(field_path, msg)
        return _MISSING

    @staticmethod
    def _assemble_value(
        field: Field[TOMLValue],
        field_path: str,
        validated: TOMLValue,
        /,
    ) -> TOMLValue:
        if isinstance(field, _Table):
            return field.schema._prepare(
                cast("Mapping[str, object]", validated),
                field_path,
            )
        if isinstance(field, ArrayOfTables):
            rows = cast("list[dict[str, TOMLValue]]", validated)
            return [
                field.schema._prepare(
                    cast("Mapping[str, object]", row),
                    f"{field_path}[{index}]",
                )
                for index, row in enumerate(rows)
            ]
        return copy.deepcopy(validated)

    def validate(self, config: Mapping[str, object], /) -> dict[str, TOMLValue]:
        return self._prepare(config, self.name or "")

    def load(self, path: str | os.PathLike[str], /) -> dict[str, TOMLValue]:
        try:
            with Path(path).open("rb") as stream:
                raw = tomllib.load(stream)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ConfigurationError(str(path), str(exc)) from exc
        return self._prepare(raw, self.name)

    # -- template rendering internals -------------------------------------

    @staticmethod
    def _constructor_names(field: Field[TOMLValue], /) -> list[str]:
        names: list[str] = []
        for cls in reversed(type(field).mro()):
            if not isinstance(cls, type) or not issubclass(cls, Field):
                continue
            constructor = cls.__dict__.get("__init__")
            if constructor is None:
                continue
            for name, parameter in inspect.signature(constructor).parameters.items():
                if name in {"self", "name", "description"} or name in names:
                    continue
                if parameter.kind is inspect.Parameter.VAR_KEYWORD:
                    continue
                names.append(name)
        return names

    @staticmethod
    def _field_options(field: Field[TOMLValue], /) -> list[str]:
        element = getattr(field, "element", None)
        type_name = type(field).__name__.lower()
        if isinstance(element, Field):
            type_name += f"[{type(element).__name__.lower()}]"

        parts: list[str] = [type_name, *Schema._own_option_parts(field)]
        if isinstance(element, Field):
            parts.extend(Schema._element_option_parts(element))
        return parts

    @staticmethod
    def _own_option_parts(field: Field[TOMLValue], /) -> list[str]:
        parts: list[str] = []
        for name in Schema._constructor_names(field):
            if not hasattr(field, name):
                continue
            value = getattr(field, name)
            if value is None:
                continue
            if name == "required":
                parts.append("required" if value else "optional")
            elif name not in {"schema", "element"}:
                if value is True:
                    displayed = "true"
                elif value is False:
                    displayed = "false"
                elif isinstance(value, type):
                    displayed = value.__name__
                else:
                    displayed = repr(value)
                parts.append(f"{name}={displayed}")
        return parts

    @staticmethod
    def _element_option_parts(element: Field[TOMLValue], /) -> list[str]:
        parts: list[str] = []
        for name in Schema._constructor_names(element):
            if name in {"required", "default", "schema", "element"} or not hasattr(
                element,
                name,
            ):
                continue
            value = getattr(element, name)
            if value is not None:
                if value is True:
                    displayed = "true"
                elif value is False:
                    displayed = "false"
                elif isinstance(value, type):
                    displayed = value.__name__
                else:
                    displayed = repr(value)
                parts.append(f"element.{name}={displayed}")
        return parts

    @staticmethod
    def _comment_block(field: Field[TOMLValue], /, *, width: int = 100) -> list[str]:
        content_width = width - 2
        description = field.description or field.name
        lines = [
            f"# {line}"
            for line in textwrap.wrap(description, width=content_width) or [""]
        ]
        parts = Schema._field_options(field)

        if not parts:
            return lines

        current = "# "
        for part in parts:
            token = part if current == "# " else f" | {part}"
            if len(current) + len(token) <= width:
                current += token
                continue

            if current != "# ":
                lines.append(current)

            wrapped = textwrap.wrap(
                part,
                width=content_width,
                break_long_words=True,
                break_on_hyphens=False,
            ) or [""]
            lines.extend(f"# {piece}" for piece in wrapped[:-1])
            current = f"# {wrapped[-1]}"

        if current != "# ":
            lines.append(current)

        return lines

    @staticmethod
    def _field_comment_lines(field: Field[TOMLValue], /) -> list[str]:
        return Schema._comment_block(field)

    @staticmethod
    def _toml_literal(value: TOMLValue, /) -> str:
        return (
            tomlkit.dumps({"value": Schema._toml_item(value)})
            .strip()
            .removeprefix("value = ")
        )

    @staticmethod
    def _section(title: str, /, *, width: int = 100) -> str:
        return "# " + f" {title} ".center(width - 2, "─")

    @staticmethod
    def _constraint_title(constraint: Constraint, /) -> str:
        if isinstance(constraint, _Constraint):
            return {
                "AllOrNone": "ALL OR NONE",
                "Exclusive": "EXCLUSIVE",
                "ExactlyOne": "EXACTLY ONE",
                "AtLeastOne": "AT LEAST ONE",
                "Requires": "REQUIRES",
                "Equal": "EQUAL",
                "NotEqual": "NOT EQUAL",
                "LessThan": "LESS THAN",
                "LessThanOrEqual": "LESS THAN OR EQUAL",
                "GreaterThan": "GREATER THAN",
                "GreaterThanOrEqual": "GREATER THAN OR EQUAL",
            }.get(constraint.name, constraint.name.upper())
        return type(constraint).__name__.upper()

    @staticmethod
    def _constraint_description(constraint: Constraint, /) -> str:
        if not isinstance(constraint, _Constraint):
            return constraint.describe()
        names = [target.name for target in constraint.targets]
        if constraint.name in _PRESENCE_DESCRIPTIONS:
            return _PRESENCE_DESCRIPTIONS[constraint.name]
        if constraint.name in _COMPARISON_DESCRIPTIONS:
            return _COMPARISON_DESCRIPTIONS[constraint.name].format(*names)
        return constraint.describe()

    @staticmethod
    def _render_field(field: Field[TOMLValue], /) -> list[str]:
        lines = Schema._field_comment_lines(field)
        if field.default is None:
            lines.append(f"{field.name} =")
        else:
            lines.append(
                f"{field.name} = {Schema._toml_literal(copy.deepcopy(field.default))}",
            )
        lines.append("")
        return lines

    @staticmethod
    def _comment_lines(text: str, /, *, width: int = 98) -> list[str]:
        return [f"# {line}" for line in textwrap.wrap(text, width=width) or [""]]

    def _template_lines(self, /, *, prefix: str = "", top: bool = False) -> list[str]:
        lines: list[str] = []
        rendered: set[str] = set()

        if top:
            lines.extend(Schema._comment_lines(self.description or self.name))
            lines.append("")

        constrained_at: dict[str, int] = {}
        for index, item in enumerate(self._items):
            if isinstance(item, Constraint):
                for target in item.targets:
                    constrained_at.setdefault(target.name, index)

        for index, item in enumerate(self._items):
            if isinstance(item, Constraint):
                lines.extend(
                    self._constraint_block_lines(
                        item,
                        index,
                        constrained_at,
                        prefix,
                        rendered,
                    ),
                )
            elif constrained_at.get(item.name, index) <= index:
                self._append_target_lines(item, prefix, rendered, lines)

        while lines and lines[-1] == "":
            lines.pop()

        return lines

    def _append_target_lines(
        self,
        target: Field[TOMLValue] | _AnySchema,
        prefix: str,
        rendered: set[str],
        lines: list[str],
        /,
    ) -> None:
        if target.name in rendered:
            return
        new_lines = self._render_target_lines(target, prefix)
        if new_lines is None:
            return
        lines.extend(new_lines)
        rendered.add(target.name)

    def _constraint_block_lines(
        self,
        item: Constraint,
        index: int,
        constrained_at: dict[str, int],
        prefix: str,
        rendered: set[str],
        /,
    ) -> list[str]:
        title = self._constraint_title(item)
        lines = [
            self._section(title),
            *Schema._comment_lines(self._constraint_description(item)),
            "",
        ]
        for target in item.targets:
            if constrained_at.get(target.name) == index:
                self._append_target_lines(target, prefix, rendered, lines)
        lines.append(self._section(f"END {title}"))
        lines.append("")
        return lines

    @staticmethod
    def _nested_block(
        comment_lines: list[str],
        header: str,
        body: list[str],
        /,
    ) -> list[str]:
        return [*comment_lines, header, *body, ""]

    def _render_target_lines(
        self,
        target: Field[TOMLValue] | _AnySchema,
        prefix: str,
        /,
    ) -> list[str] | None:
        table_name = f"{prefix}.{target.name}" if prefix else target.name
        if isinstance(target, Schema):
            field = self._fields[target.name]
            if not isinstance(field, _Table) or field.schema is not target:
                return None
            return self._nested_block(
                Schema._comment_lines(target.description or target.name),
                f"[{table_name}]",
                target._template_lines(prefix=table_name),
            )
        if isinstance(target, _Table):
            return self._nested_block(
                Schema._comment_lines(target.description or target.name),
                f"[{table_name}]",
                target.schema._template_lines(prefix=table_name),
            )
        if isinstance(target, ArrayOfTables):
            return self._nested_block(
                self._field_comment_lines(target),
                f"[[{table_name}]]",
                target.schema._template_lines(prefix=table_name),
            )
        return self._render_field(target)

    # -- template output ---------------------------------------------------

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

        content = "\n".join(self._template_lines(top=True)) + "\n"
        self._atomic_write(target, content, parents=False)

    @staticmethod
    def _toml_item(value: TOMLValue, /) -> object:
        if type(value) is dict:
            item = tomlkit.inline_table()
            for key, nested in value.items():
                item[key] = Schema._toml_item(nested)
            return item
        if type(value) is list:
            array = tomlkit.array()
            for nested in value:
                array.append(Schema._toml_item(nested))
            return array
        return value

    @staticmethod
    def _atomic_write(
        path: Path,
        content: str,
        /,
        *,
        parents: bool = True,
    ) -> None:
        if parents:
            path.parent.mkdir(parents=True, exist_ok=True)
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            if path.exists():
                temporary.chmod(path.stat().st_mode & 0o777)
            temporary.replace(path)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()


# Alias used for parameter annotations that need to reference the `Schema`
# class generically. The class itself defines a builder method literally
# named `Schema` (see `Schema.Schema`), which shadows the class name within
# its own body for type-checking purposes; this alias avoids that ambiguity.
_AnySchema = Schema
