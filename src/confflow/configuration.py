from __future__ import annotations

import os
import re
import tomllib
from collections.abc import Iterator, Mapping
from datetime import date, datetime, time
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

from confflow.core.definitions.base import Definition
from confflow.core.errors import REDACTED_VALUE, SchemaError, ValidationError
from confflow.core.schemas import (
    Array,
    Mapping as MappingSchema,
    NestedArray,
    Table,
    TableArray,
)
from confflow.core.schemas.base import Schema
from confflow.core.schemas.scalars.base import Scalar
from confflow.render import render_template

_ENVIRONMENT_REFERENCE = re.compile(r"(\$\$?)([A-Za-z_][A-Za-z0-9_]*)")


class Configuration:
    __slots__ = ("__root",)

    def __init__(
        self, name: str, description: str | None, /, *schemas: Schema[Any]
    ) -> None:
        if any(not isinstance(schema, Schema) for schema in schemas):
            raise SchemaError("root schemas must be Schema objects")
        self.__root: Final[Table] = Table(name, description, *schemas)

    def template(
        self,
        destination: str | Path,
        /,
        *,
        overwrite: bool = False,
        parents: bool = False,
    ) -> Path:
        destination = Path(destination)
        if destination.is_dir():
            destination = destination / f"{self.__root.name.lower()}.toml"
        if parents:
            destination.parent.mkdir(parents=True, exist_ok=True)

        content = render_template(
            self.__root.name,
            self.__root.description,
            self.__root.schemas,
        )
        with destination.open("w" if overwrite else "x", encoding="utf-8") as file:
            file.write(content)
        return destination

    def load(self, source: str | Path, /) -> Mapping[str, object]:
        source = Path(source)

        with source.open("rb") as file:
            value = tomllib.load(file)
        value = _resolve_table(self.__root, value, ())
        self.__root.validate(value)

        return _freeze_mapping(value, self.__root)


def _resolve_table(
    schema: Table, value: Mapping[str, object], path: tuple[str | int, ...]
) -> dict[str, object]:
    schemas = {child.name: child for child in schema.schemas}
    return {
        key: _resolve_environment(schemas[key], item, (*path, key))
        if key in schemas
        else item
        for key, item in value.items()
    }


def _resolve_environment(
    schema: Schema[Any], value: object, path: tuple[str | int, ...]
) -> object:
    if isinstance(value, str):
        definition = schema.definition if isinstance(schema, Scalar) else None
        try:
            return _resolve_string(value, definition, path)
        except ValidationError as error:
            if isinstance(schema, Scalar) and schema.secret:
                error.redact(value)
                raise error from None
            raise
    if isinstance(schema, Table) and isinstance(value, Mapping):
        return _resolve_table(schema, value, path)
    if isinstance(schema, MappingSchema) and isinstance(value, Mapping):
        return {
            key: _resolve_environment(schema.value, item, (*path, f"[{key!r}]"))
            for key, item in value.items()
        }
    if isinstance(value, list):
        if isinstance(schema, (TableArray, NestedArray)):
            item_schema = (
                schema.table if isinstance(schema, TableArray) else schema.array
            )
            return [
                _resolve_environment(item_schema, item, (*path, index))
                for index, item in enumerate(value)
            ]
        if isinstance(schema, Array):
            definition = getattr(schema, "definition", None)
            if isinstance(definition, Definition):
                return [
                    _resolve_string(item, definition, (*path, index))
                    if isinstance(item, str)
                    else item
                    for index, item in enumerate(value)
                ]
    return value


def _resolve_string(
    value: str,
    definition: Definition[Any] | None,
    path: tuple[str | int, ...],
) -> object:
    match = _ENVIRONMENT_REFERENCE.fullmatch(value)
    if match is None:
        return value
    prefix, name = match.groups()
    if prefix == "$$":
        return f"${name}"
    if definition is None:
        raise ValidationError(
            "environment references are only supported for scalar values",
            path=path,
            value=value,
            expected="scalar environment reference",
        )
    try:
        environment_value = os.environ[name]
    except KeyError as error:
        raise ValidationError(
            f"environment variable {name!r} is not set",
            path=path,
            value=value,
        ) from error
    try:
        return _convert_environment(environment_value, definition.VALUE_TYPE)
    except ValueError as error:
        raise ValidationError(
            f"environment variable {name!r} cannot be converted to "
            f"{definition.VALUE_TYPE.__name__}",
            path=path,
            value=value,
            expected=definition.VALUE_TYPE.__name__,
        ) from error


def _convert_environment(value: str, value_type: type[object]) -> object:
    if value_type is str:
        return value
    if value_type is bool:
        if value not in ("true", "false"):
            raise ValueError("expected true or false")
        return value == "true"
    if value_type in (int, float):
        return value_type(value)
    if value_type is date:
        return date.fromisoformat(value)
    if value_type is time:
        return time.fromisoformat(value)
    if value_type is datetime:
        return datetime.fromisoformat(value)
    raise ValueError("unsupported environment scalar type")


class _SecretMapping(Mapping[str, object]):
    __slots__ = ("__secrets", "__values")

    def __init__(self, values: Mapping[str, object], secrets: frozenset[str]) -> None:
        self.__values = MappingProxyType(dict(values))
        self.__secrets = secrets

    def __getitem__(self, key: str) -> object:
        return self.__values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.__values)

    def __len__(self) -> int:
        return len(self.__values)

    def __repr__(self) -> str:
        return repr(
            MappingProxyType(
                {
                    key: REDACTED_VALUE if key in self.__secrets else item
                    for key, item in self.__values.items()
                }
            )
        )


def _mapping_schema(schema: Schema[Any] | None, key: str) -> Schema[Any] | None:
    if isinstance(schema, Table):
        return next((child for child in schema.schemas if child.name == key), None)
    if isinstance(schema, MappingSchema):
        return schema.value
    return None


def _freeze_mapping(
    value: Mapping[str, object], schema: Schema[Any] | None = None
) -> Mapping[str, object]:
    values: dict[str, object] = {}
    secrets: set[str] = set()
    for key, item in value.items():
        child = _mapping_schema(schema, key)
        values[key] = _freeze_value(item, child)
        if isinstance(child, Scalar) and child.secret:
            secrets.add(key)
    if secrets:
        return _SecretMapping(values, frozenset(secrets))
    return MappingProxyType(values)


def _freeze_value(value: object, schema: Schema[Any] | None = None) -> object:
    if isinstance(value, Mapping):
        return _freeze_mapping(value, schema)
    if isinstance(value, list):
        child = None
        if isinstance(schema, TableArray):
            child = schema.table
        elif isinstance(schema, NestedArray):
            child = schema.array
        return tuple(_freeze_value(item, child) for item in value)
    return value
