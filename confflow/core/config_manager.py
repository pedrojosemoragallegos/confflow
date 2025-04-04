from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from confflow.utils.types import PathLike

from ..formatter.factory import formatter_factory
from ..utils.types import BaseConfig, ConfigGroup, SchemaMap

# from .config_handler import ConfigHandler
from .config_loader import load_configuration
from .config_saver import save_configuration
from .schema_registry import SchemaRegistry


class ConfigManager:
    def __init__(self):
        self._schema_map: SchemaMap = SchemaMap()
        self._schema_registry: SchemaRegistry = SchemaRegistry()
        self._mutually_exclusive_groups: Optional[List[ConfigGroup]] = None

    def register_schemas(self, *configs: BaseConfig):
        self._schema_registry.register_schemas(*configs)

    def set_mutual_exclusive_groups(self, *exclusive_config_groups: ConfigGroup):
        all_exclusive_configs: Set[BaseConfig] = {
            config
            for exclusive_config_group in exclusive_config_groups
            for config in exclusive_config_group
        }

        registered_configs: Set[BaseConfig] = set(self._schema_registry.values())

        unregistered_configs: Set[BaseConfig] = all_exclusive_configs.difference(
            registered_configs
        )

        if unregistered_configs:
            raise ValueError(
                f"The following classes are not valid: "
                f"{', '.join(cls.__name__ for cls in unregistered_configs)}"
            )

        for exclusive_config_group in exclusive_config_groups:
            active_classes: List[BaseConfig] = [
                config_class
                for config_class in self._schema_map.values()
                if config_class in exclusive_config_group
            ]

            if len(active_classes) > 1:
                raise ValueError(
                    f"Mutual exclusion conflict: {active_classes} are active in group {exclusive_config_group}."
                )

        self._mutually_exclusive_groups: List[ConfigGroup] = exclusive_config_groups

    def load_yaml(self, input_path: PathLike):
        load_configuration(
            type="yaml",
            input_path=input_path,
            mutually_exclusive_groups=self._mutually_exclusive_groups,
            configurations=self._schema_map,
            schema_registry=self._schema_registry,
        )

    def to_yaml(self, output_path: PathLike):
        if not self._schema_map:
            raise ValueError("No configurations loaded to save.")

        output_path: Path = Path(output_path)

        default_values: Dict[str, Dict[str, Any]] = {  # TODO check typing
            config.__class__.__name__: config.model_dump()
            for config in self._schema_map.values()
        }

        data: str = formatter_factory(type="yaml").generate(
            schemas=self._schema_registry.values(),
            default_values=default_values,
        )

        save_configuration(type="yaml", output_path=output_path, data=data)

    def create_template(
        self, output_path: PathLike
    ):  # TODO pass type="yaml | json ..."
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

        data: str = formatter_factory(type="yaml").generate(
            schemas=self._schema_registry.values(),
            header=HEADER,
            mutually_exclusive_groups=self._mutually_exclusive_groups,
        )

        save_configuration(type="yaml", output_path=output_path, data=data)

    def __getitem__(self, name: str):  # -> ConfigHandler:
        return self._schema_map[name].model_dump(mode="python")
        # if name not in self._schema_map:
        #     raise ValueError(f"Configuration for '{name}' is not loaded.")
        # return ConfigHandler(name, self)
