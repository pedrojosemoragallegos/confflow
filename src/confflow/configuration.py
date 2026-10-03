from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from confflow.core.errors import SchemaError
from confflow.core.schemas import Table
from confflow.core.schemas.base import Schema
from confflow.loader import load_configuration
from confflow.render import render_template

if TYPE_CHECKING:
    from collections.abc import Mapping


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
            destination: Path = destination / f"{self.__root.name.lower()}.toml"

        if parents:
            destination.parent.mkdir(parents=True, exist_ok=True)

        content: str = render_template(
            self.__root.name, self.__root.description, self.__root.schemas
        )

        with destination.open(mode="w" if overwrite else "x", encoding="utf-8") as file:
            file.write(content)

        return destination

    def load(self, source: str | Path, /) -> Mapping[str, object]:
        return load_configuration(self.__root, source)
