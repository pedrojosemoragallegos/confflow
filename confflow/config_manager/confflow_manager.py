from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel as BaseConfig

from confflow.types import PathLike

from ..yaml_creator.yaml_creator import create_yaml
from .config_handler import ConfigHandler
from .config_loader import load_configuration
from .config_saver import save_configuration
from .mutual_exclusion_validator import is_mutual_exclusive
from .registry_validator import validate_config_classes
from .schema_registry import SchemaRegistry


class ConfflowManager:
    def __init__(self):
        self._configurations: OrderedDict[str, BaseConfig] = {}
        self._schema_registry: SchemaRegistry = SchemaRegistry()
        self._mutually_exclusive_groups: Optional[List[List[BaseConfig]]] = None

    def register_schemas(self, *args: Type[BaseConfig]):
        self._schema_registry.register_schemas(*args)

    def set_mutual_exclusive_groups(self, *config_classes: List[Type[BaseConfig]]):
        validate_config_classes(
            self._schema_registry,
            *[config_class for group in config_classes for config_class in group],
        )
        is_mutual_exclusive(
            config_classes=self._configurations.values(),
            exclusive_groups=config_classes,
        )
        self._mutually_exclusive_groups: List[List[BaseConfig]] = config_classes

    def load_yaml(self, input_path: PathLike):
        load_configuration(
            type="yaml",
            input_path=input_path,
            mutually_exclusive_groups=self._mutually_exclusive_groups,
            configurations=self._configurations,
            schema_registry=self._schema_registry,
        )

    def to_yaml(self, output_path: PathLike):
        if not self._configurations:
            raise ValueError("No configurations loaded to save.")

        output_path: Path = Path(output_path)

        default_values: Dict[str, Dict[str, Any]] = {  # TODO check typing
            config.__class__.__name__: config.model_dump()
            for config in self._configurations.values()
        }

        data: str = create_yaml(
            schemas=self._schema_registry.values(),
            default_values=default_values,
        )

        save_configuration(type="yaml", output_path=output_path, data=data)

    def create_template(self, output_path: PathLike):
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
            "# ================================================================================\n\n",
        ]

        data: str = create_yaml(
            schemas=self._schema_registry.values(),
            header=HEADER,
            mutually_exclusive_groups=self._mutually_exclusive_groups,
        )

        save_configuration(type="yaml", output_path=output_path, data=data)

    def __getitem__(self, name: str) -> ConfigHandler:
        if name not in self._configurations:
            raise ValueError(f"Configuration for '{name}' is not loaded.")
        return ConfigHandler(name, self)
