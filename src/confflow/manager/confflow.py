from __future__ import annotations

import typing

from confflow.mixins import IPythonMixin

if typing.TYPE_CHECKING:
    from collections.abc import ItemsView, KeysView, ValuesView

    from confflow.config import Config
    from confflow.types import ValueTypes


class Confflow(IPythonMixin):
    def __init__(self, *configs: Config) -> None:
        self._configs: dict[str, Config] = {config.name: config for config in configs}

    def keys(self) -> KeysView[str]:
        return self._configs.keys()

    def values(self) -> ValuesView[Config]:
        return self._configs.values()

    def items(self) -> ItemsView[str, Config]:
        return self._configs.items()

    def __getitem__(self, key: str) -> Config | ValueTypes:
        if key not in self._configs:
            raise KeyError(  # noqa: TRY003
                f"Config section '{key}' not found. "  # noqa: EM102
                f"Available sections: {list(self._configs.keys())}",
            )
        return self._configs[key]

    def __contains__(self, key: str) -> bool:
        return key in self._configs

    def __len__(self) -> int:
        return len(self._configs)

    def __repr__(self) -> str:
        return f"AppConfig(sections={list(self._configs.keys())})"
