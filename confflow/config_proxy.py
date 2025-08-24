from __future__ import annotations

from typing import TYPE_CHECKING, Any, ItemsView, KeysView, Union, ValuesView

if TYPE_CHECKING:
    from .manager import Manager

from .core import Config


class ConfigProxy:
    def __init__(self, manager: Manager) -> None:
        self._manager: Manager = manager
        for config_name in manager.keys():
            config_obj: Config = manager[config_name]
            setattr(self, config_name, ConfigSectionView(config_obj))

    def __getitem__(self, key: str) -> Config:
        return self._manager[key]

    def __contains__(self, key: str) -> bool:
        return key in self._manager

    def keys(self) -> KeysView[str]:
        return self._manager.keys()

    def values(self) -> ValuesView[Config]:
        return self._manager.values()

    def items(self) -> ItemsView[str, Config]:
        return self._manager.items()


class ConfigSectionView:
    def __init__(self, config_obj: Config) -> None:
        self._config: Config = config_obj
        for key in config_obj.keys():
            value: Union[Config, Any] = config_obj[key]
            if isinstance(value, Config):
                setattr(self, key, ConfigSectionView(value))
            else:
                setattr(self, key, value)

    def __getitem__(self, key: str) -> Any:
        return self._config[key]

    def __contains__(self, key: str) -> bool:
        return key in self._config
