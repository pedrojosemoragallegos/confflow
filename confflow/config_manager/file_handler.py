from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union

import yaml
from pydantic import BaseModel as BaseConfig

from confflow.config_manager.schema_registry import SchemaRegistry
from confflow.types import ensure_path
from confflow.yaml_creator.yaml_creator import create_yaml


@ensure_path
def load_yaml(
    input_path: Union[str, Path],
    mutually_exclusive_groups: List[List[BaseConfig]],
    configurations: OrderedDict[str, BaseConfig],
    schema_registry: SchemaRegistry,
):
    raw_configs: Dict[str, Dict[str, Any]]

    with input_path.open("r") as file:
        raw_configs: Dict[str, Any] = yaml.safe_load(file)

    loaded_config_names: Set[str] = set(raw_configs.keys())

    if mutually_exclusive_groups:
        for group in mutually_exclusive_groups:
            group: List[str] = [cls.__name__ for cls in group]
            active_configs: List[str] = [
                name for name in group if name in loaded_config_names
            ]
            if len(active_configs) > 1:
                raise ValueError(
                    f"Mutually exclusive conflict: Multiple configurations from the group {group} are loaded: {active_configs}"
                )

    for config_name, config_data in raw_configs.items():
        config_class: Optional[Type[BaseConfig]] = schema_registry[config_name]
        if not config_class:
            raise ValueError(f"Unknown config type: {config_name}")

        configurations[config_name] = config_class(**config_data)


@ensure_path
def save_config(
    output_path: Union[str, Path],
    schema_registry: SchemaRegistry,
    configurations: OrderedDict[str, BaseConfig],
    header: Optional[str] = None,
):
    default_values: Dict[str, Dict[str, Any]] = {
        config.__class__.__name__: config.model_dump()
        for config in configurations.values()
    }

    with open(output_path, "w") as yaml_file:
        yaml_file.write(
            create_yaml(
                schemas=schema_registry.values(),
                default_values=default_values,
                header=header,
            )
        )
