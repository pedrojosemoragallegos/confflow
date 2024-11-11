from collections import OrderedDict
from pathlib import Path
from typing import List, Optional, Type, Union

from pydantic import BaseModel as BaseConfig

from confflow.types import ensure_path

from .config_handler import ConfigHandler
from .file_handler import load_yaml, save_config
from .mutual_exclusion_validator import is_mutual_exclusive
from .registry_validator import validate_config_classes
from .schema_registry import SchemaRegistry


class ConfflowManager:
    def __init__(self):
        self._configs: OrderedDict[str, BaseConfig] = {}
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
            config_classes=self._configs.values(),
            exclusive_groups=config_classes,
        )
        self._mutually_exclusive_groups: List[List[BaseConfig]] = config_classes

    @ensure_path
    def load_yaml(self, input_path: Union[str, Path]):
        load_yaml(
            input_path=input_path,
            mutually_exclusive_groups=self._mutually_exclusive_groups,
            configurations=self._configs,
            schema_registry=self._schema_registry,
        )

    @ensure_path
    def save_config(self, output_path: Union[str, Path]):
        if not self._configs:
            raise ValueError("No configurations loaded to save.")

        save_config(
            output_path=output_path,
            schema_registry=self._schema_registry,
            configurations=self._configs,
        )

    @ensure_path
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
            "# ================================================================================\n\n",
        ]

        save_config(
            output_path=output_path,
            schema_registry=self._schema_registry,
            configurations=self._configs,
            header=HEADER,
        )

    def __getitem__(self, name: str) -> ConfigHandler:
        if name not in self._configs:
            raise ValueError(f"Configuration for '{name}' is not loaded.")
        return ConfigHandler(name, self)
