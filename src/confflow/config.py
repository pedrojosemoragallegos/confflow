from __future__ import annotations

import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final

from confflow.core.errors import SchemaError, ValidationError
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

    @property
    def name(self) -> str:
        return self.__root.name

    @property
    def description(self) -> str | None:
        return self.__root.description

    @property
    def schemas(self) -> tuple[Schema[Any], ...]:
        return self.__root.schemas

    def validate(self, value: Mapping[str, object], /) -> None:
        if not isinstance(value, Mapping):
            raise ValidationError(
                "configuration must be a mapping",
                value=value,
                expected="configuration mapping",
            )

        self.__root.validate(value)

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
            destination = destination / f"{self.name.lower()}.toml"
        if parents:
            destination.parent.mkdir(parents=True, exist_ok=True)

        content = render_template(self.name, self.description, self.schemas)
        with destination.open("w" if overwrite else "x", encoding="utf-8") as file:
            file.write(content)
        return destination

    def load(self, source: str | Path) -> Mapping[str, object]:
        source = Path(source)
        with source.open("rb") as file:
            value = tomllib.load(file)
        self.validate(value)
        return value
