from typing import Iterator, Union

from ..config import Config
from ..mixins import IPythonMixin
from ..types import Value


class Confflow(IPythonMixin):
    def __init__(self, *configs: Config):
        self._configs: dict[str, Config] = {config.name: config for config in configs}

    def keys(self) -> Iterator[str]:
        return iter(self._configs.keys())

    def values(self) -> Iterator[Config]:
        return iter(self._configs.values())

    def items(self) -> Iterator[tuple[str, Config]]:
        return iter(self._configs.items())

    def __getitem__(self, key: str) -> Union[Config, Value]:
        if key not in self._configs:
            available_keys: list[str] = list(self._configs.keys())
            raise KeyError(
                f"Config section '{key}' not found. "
                f"Available sections: {available_keys}"
            )
        return self._configs[key]

    def __contains__(self, key: str) -> bool:
        return key in self._configs

    def __len__(self) -> int:
        return len(self._configs)

    def __repr__(self) -> str:
        return f"AppConfig(sections={list(self._configs.keys())})"
