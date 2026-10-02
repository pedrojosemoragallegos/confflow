from __future__ import annotations

import tomllib
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

from confflow.core.errors import SchemaError
from confflow.core.schemas import Table
from confflow.core.schemas.base import Schema
from confflow.render import render_template


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
        self.__root.validate(value)

        return _freeze_mapping(value)


def _freeze_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType({key: _freeze_value(item) for key, item in value.items()})


def _freeze_value(value: object) -> object:
    if isinstance(value, Mapping):
        return _freeze_mapping(value)
    if isinstance(value, list):
        return tuple(_freeze_value(item) for item in value)
    return value
