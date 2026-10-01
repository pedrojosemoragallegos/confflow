from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final, cast, final

from typing_extensions import override

from .core._composition_validation import validate_composition
from .core._validators import validate_configuration
from .core.definitions._validators import validate_name
from .parser import parse
from .renderer import render
from .utils.freeze import freeze_configuration

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .core.entries.base import Entry
    from .core.rules.base import Rule
    from .types import ConfigurationData


@final
class Configuration:
    __slots__ = ("__description", "__entries", "__name", "__rules")

    def __init__(
        self,
        name: str,
        description: str,
        /,
        *members: Entry,
        rules: Iterable[Rule] | None = None,
    ) -> None:
        validate_name(value=name, label="configuration name")
        self.__name: Final[str] = name
        self.__description: Final[str] = description
        self.__entries, self.__rules = validate_composition(
            members, rules, label="configuration", recursive=True
        )

    def template(self, path: str | Path, /, *, overwrite: bool = False) -> None:
        if type(overwrite) is not bool:
            raise TypeError("overwrite must be a boolean")

        directory = Path(path)
        if not directory.exists():
            raise FileNotFoundError(f"template directory does not exist: {directory}")
        if not directory.is_dir():
            raise NotADirectoryError(f"template path is not a directory: {directory}")

        target = directory / f"{self.__name.lower()}.toml"
        if target.exists():
            if target.is_dir():
                raise IsADirectoryError(f"template path is a directory: {target}")
            if not overwrite:
                raise FileExistsError(f"template file already exists: {target}")

        target.write_text(
            render(self.__name, self.__description, self.__entries, self.__rules),
            encoding="utf-8",
        )

    def load(self, path: str | Path, /) -> ConfigurationData:
        source = Path(path)
        if not source.exists():
            raise FileNotFoundError(f"configuration file does not exist: {source}")
        if not source.is_file():
            raise IsADirectoryError(f"configuration path is not a file: {source}")
        if source.suffix.lower() != ".toml":
            raise ValueError("configuration file must use .toml")

        data = parse(source)
        validate_configuration(self.__entries, self.__rules, data)
        if not isinstance(data, dict):
            raise TypeError("configuration loader must return a dictionary")
        return freeze_configuration(self.__entries, cast("dict[str, object]", data))

    @override
    def __repr__(self) -> str:
        return (
            f"Configuration(name={self.__name!r}, description={self.__description!r}, "
            f"entries={self.__entries!r}, rules={self.__rules!r})"
        )
