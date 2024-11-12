from collections import OrderedDict
from pathlib import Path
from typing import List, Literal, Optional, Set, Type

from pydantic import BaseModel as BaseConfig

from confflow.config_manager.schema_registry import SchemaRegistry
from confflow.file_handler.factory import file_hanlder_factory
from confflow.types import ParsedData, PathLike


def load_configuration(
    type: Literal["yaml"],
    input_path: PathLike,
    mutually_exclusive_groups: List[List[BaseConfig]],
    configurations: OrderedDict[str, BaseConfig],
    schema_registry: SchemaRegistry,
):
    input_path: Path = Path(input_path)
    parsed_data: ParsedData = file_hanlder_factory(type).load(input_path)
    loaded_config_names: Set[str] = set(parsed_data.keys())

    if mutually_exclusive_groups:
        for group in mutually_exclusive_groups:
            group: List[str] = [cls.__name__ for cls in group]
            active_configurations: List[str] = [
                name for name in group if name in loaded_config_names
            ]
            if len(active_configurations) > 1:
                raise ValueError(
                    f"Mutually exclusive conflict: Multiple configurations from the group {group} are loaded: {active_configurations}"
                )

    for config_name, config_data in parsed_data.items():
        config_class: Optional[Type[BaseConfig]] = schema_registry[config_name]
        if not config_class:
            raise ValueError(f"Unknown config type: {config_name}")

        configurations[config_name] = config_class(**config_data)
