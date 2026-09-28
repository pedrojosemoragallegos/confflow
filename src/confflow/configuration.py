from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final, cast, final

from typing_extensions import override

from .core.schema import Schema
from .core.validator import validate
from .parser import parse
from .renderer import render
from .utils.freeze import freeze_configuration

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .core.members.base import Entry
    from .core.rules.base import Rule
    from .types import ConfigurationData


@final
class Configuration:
    __slots__ = ("__schema",)

    def __init__(
        self,
        name: str,
        description: str,
        /,
        *members: Entry,
        rules: Iterable[Rule] = (),
    ) -> None:
        self.__schema: Final[Schema] = Schema(name, description, *members, rules=rules)

    def template(self, path: str | Path, /, *, overwrite: bool = False) -> None:
        if type(overwrite) is not bool:
            raise TypeError("overwrite must be a boolean")

        directory = Path(path)
        if not directory.exists():
            raise FileNotFoundError(f"template directory does not exist: {directory}")
        if not directory.is_dir():
            raise NotADirectoryError(f"template path is not a directory: {directory}")

        target = directory / f"{self.__schema.name.lower()}.toml"
        if target.exists():
            if target.is_dir():
                raise IsADirectoryError(f"template path is a directory: {target}")
            if not overwrite:
                raise FileExistsError(f"template file already exists: {target}")

        target.write_text(render(self.__schema), encoding="utf-8")

    def load(self, path: str | Path, /) -> ConfigurationData:
        source = Path(path)
        if not source.exists():
            raise FileNotFoundError(f"configuration file does not exist: {source}")
        if not source.is_file():
            raise IsADirectoryError(f"configuration path is not a file: {source}")
        if source.suffix.lower() != ".toml":
            raise ValueError("configuration file must use .toml")

        data = parse(source)
        validate(self.__schema, data)
        if not isinstance(data, dict):
            raise TypeError("configuration loader must return a dictionary")
        return freeze_configuration(self.__schema, cast("dict[str, object]", data))

    @override
    def __repr__(self) -> str:
        return f"Configuration(schema={self.__schema!r})"
