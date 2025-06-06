from typing import Iterator, Optional

from .config import Config


class ConfigManager:
    def __init__(self, *configs: Config):
        self._configs = {}
        for config in configs:
            name = config._name
            if name in self._configs:
                raise ValueError(f"Duplicate config name '{name}' detected.")
            self._configs[name] = config
        self._fields = self._configs  # for iPython-like access symmetry

    def get_config(self, name: str) -> Optional[Config]:
        return self._configs.get(name)

    def has_config(self, name: str) -> bool:
        return name in self._configs

    def list_configs(self) -> list[str]:
        return list(self._configs.keys())

    def __getitem__(self, name: str) -> Config:
        return self._configs[name]

    def __contains__(self, name: str) -> bool:
        return name in self._configs

    def __iter__(self) -> Iterator[str]:
        return iter(self._configs)

    def __len__(self) -> int:
        return len(self._configs)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"configs={[name for name in self._configs.keys()]!r})"
        )

    def _ipython_key_completions_(self) -> list[str]:
        return list(self._fields.keys())
