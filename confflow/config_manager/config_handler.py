from typing import Any, Dict


class ConfigHandler:
    def __init__(self, name: str, manager: "ConfflowManager") -> None:  # type: ignore  # noqa: F821 # circular import
        super().__setattr__("name", name)
        super().__setattr__("_manager", manager)

    def __getattr__(self, item: str) -> Any:
        config = self._get_config()
        if item not in config:
            raise AttributeError(
                f"Attribute '{item}' not found in the '{self.name}' configuration."
            )
        return config[item]

    def __setattr__(self, key: str, value: Any) -> None:
        config = self._get_config()
        if key not in config:
            raise AttributeError(
                f"Cannot set value for unknown attribute '{key}' in '{self.name}' configuration."
            )
        self._manager._update(self.name, **{key: value})

    def __getitem__(self, key: str) -> Any:
        try:
            return self.__getattr__(key)
        except AttributeError as e:
            raise KeyError(str(e))

    def __setitem__(self, key: str, value: Any) -> None:
        self.__setattr__(key, value)

    def _get_config(self) -> Dict[str, Any]:
        config = self._manager._configurations.get(self.name)
        if not config:
            raise ValueError(f"Configuration for '{self.name}' is not loaded.")
        return config

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default
