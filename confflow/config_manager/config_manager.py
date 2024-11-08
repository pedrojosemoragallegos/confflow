import itertools
from collections import OrderedDict
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import yaml
from pydantic import BaseModel

from ..yaml_creator import create_yaml
from .config import Config


class ConfigProxy:
    def __init__(self, name: str, manager: "ConfigManager") -> None:
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
        config = self._manager._configs.get(self.name)
        if not config:
            raise ValueError(f"Configuration for '{self.name}' is not loaded.")
        return config

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default


def singleton(cls: Type) -> Type:
    instances: Dict[Type, Any] = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class ConfigManager:
    def __init__(self):
        self._schema_map: OrderedDict[str, BaseModel] = OrderedDict()
        self._configs: OrderedDict[str, BaseModel] = {}
        self._mutually_exclusive_groups: Optional[List[List[str]]] = None

    def register_schemas(self, *args: Type[BaseModel]):
        for schema_class in args:
            if not issubclass(schema_class, BaseModel):
                raise TypeError(
                    f"{schema_class} must be a subclass of Pydantic BaseModel."
                )

            class_name: str = schema_class.__name__
            if class_name in self._schema_map:
                raise ValueError(f"Schema '{class_name}' is already registered.")

            self._schema_map[class_name] = schema_class

    def set_mutual_exclusive_groups(self, *args: List[str]):
        def has_conflicting_groups(groups: List[List[str]]) -> bool:
            for group1, group2 in itertools.combinations(groups, 2):
                if not set(group1).isdisjoint(group2):
                    return True
            return False

        groups = list(args)  # Convert *args to a list of lists
        flattened_groups: List[str] = [item for sublist in groups for item in sublist]
        self._validate_config_classes(flattened_groups)

        if len(flattened_groups) != len(set(flattened_groups)):
            raise ValueError("Duplicate items found in mutually exclusive groups.")

        if has_conflicting_groups(groups):
            raise ValueError("Logical conflicts detected in mutually exclusive groups.")

        self._mutually_exclusive_groups = groups

    def load_yaml(self, input_path: Path):
        raw_configs: Dict[str, Dict[str, Any]]

        with input_path.open("r") as file:
            raw_configs = yaml.safe_load(file)

        loaded_config_names = set(raw_configs.keys())

        if self._mutually_exclusive_groups:
            for group in self._mutually_exclusive_groups:
                active_configs = [name for name in group if name in loaded_config_names]
                if len(active_configs) > 1:
                    raise ValueError(
                        f"Mutually exclusive conflict: Multiple configurations from the group {group} are loaded: {active_configs}"
                    )

        for config_name, config_data in raw_configs.items():
            config_class: Optional[Type[Config]] = self._schema_map.get(config_name)
            if not config_class:
                raise ValueError(f"Unknown config type: {config_name}")

            self._configs[config_name] = config_class(**config_data)

    def save_config(self, output_path: Path):
        if not self._configs:
            raise ValueError("No configurations loaded to save.")

        with open(output_path, "w") as yaml_file:
            yaml_file.write(
                create_yaml(schema_map=self._schema_map, configs=self._configs)
            )

    def create_template(self, output_path: Path):
        HEADER: List[str] = [
            "# ================================================================================",
            "#                                   Configuration Template                        ",
            "# ================================================================================",
            "# ",
            "# Purpose:",
            "#   - Use this template to set up configuration values for your environment.",
            "#",
            "# Instructions:",
            "#   - Fill in each field with appropriate values.",
            "#   - Refer to the documentation for detailed descriptions of each field.",
            "#",
            "# Notes:",
            "#   - Only one configuration per mutually exclusive group can be active at a time.",
            "#   - Ensure data types match the specified type for each field.",
            "#",
            "# ================================================================================",
            "",
        ]

        with open(output_path, "w") as yaml_file:
            yaml_file.write(
                create_yaml(
                    schemas=list(self._schema_map.values()),
                    header=HEADER,
                )
            )

    def _is_valid_class(self, class_name: str) -> bool:
        return class_name in self._schema_map

    def _validate_config_classes(self, class_names: List[str]):
        invalid_classes: List[str] = [
            class_name
            for class_name in class_names
            if not self._is_valid_class(class_name)
        ]

        if invalid_classes:
            raise ValueError(
                f"The following classes are not valid: {', '.join(invalid_classes)}"
            )

    def __getitem__(self, name: str) -> ConfigProxy:
        if name not in self._configs:
            raise ValueError(f"Configuration for '{name}' is not loaded.")
        return ConfigProxy(name, self)
