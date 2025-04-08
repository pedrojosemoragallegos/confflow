from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from ..io import to_file
from ..utils.types import PathLike, SchemaGroup
from .exclusive_schema_manager import ExclusiveSchemaManager
from .schema_registry import SchemaRegistry

TEMPLE_HEADER: List[str] = [
    "================================================================================",
    "                                  Configuration Template                        ",
    "================================================================================",
    "",
    "Purpose:",
    "  - Use this template to set up configuration values for your environment.",
    "",
    "Instructions:",
    "  - Fill in each field with appropriate values.",
    "  - Refer to the documentation for detailed descriptions of each field.",
    "",
    "Notes:",
    "  - Only one configuration per mutually exclusive group can be active at a time.",
    "  - Ensure data types match the specified type for each field.",
    "",
    "================================================================================",
]


class ConfigManager:
    _instance: Optional["ConfigManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._schema_registry = SchemaRegistry()
            self._exclusivity_manager = ExclusiveSchemaManager()
            self._configurations: Dict[str, BaseModel] = {}
            ConfigManager._initialized = True

    def register_schema(
        self,
        schema: Type[BaseModel],
        description: Optional[str] = None,
        exclusive_group: Optional[str] = None,
    ) -> None:
        self._schema_registry.register(schema=schema, description=description)

        if exclusive_group:
            self._exclusivity_manager.add_to_group(
                group_name=exclusive_group, schema=schema
            )

    def set_configs(self, *instances: BaseModel) -> None:
        for instance in instances:
            name: str = instance.__class__.__name__

            if name not in self._schema_registry:
                raise ValueError(f"Schema '{name}' is not registered.")

            self._configurations[name] = instance

        self._exclusivity_manager.validate(list(self._configurations.values()))

    @property
    def configurations(self) -> Dict[str, BaseModel]:
        return self._configurations

    @property
    def schemas(self) -> List[BaseModel]:
        return self._schema_registry.schemas

    @property
    def exclusive_groups(self) -> List[SchemaGroup]:
        return self._exclusivity_manager.exclusive_groups

    # def load_yaml(self, input_path: PathLike):
    #     load_configuration(
    #         type="yaml",
    #         input_path=input_path,
    #         mutually_exclusive_groups=self._mutually_exclusive_groups,
    #         configurations=self._schema_map,
    #         schema_registry=self._schema_registry,
    #     )

    def save(self, output_path: PathLike):
        output_path: Path = Path(output_path)

        if not self._configurations:
            raise ValueError("No configurations to save.")

        config_values: Dict[str, Dict[str, Any]] = {  # TODO check typing
            config.__class__.__name__: config.model_dump()
            for config in self._configurations.values()
        }

        schemas: List[BaseModel] = [
            schema
            for schema in self.schemas
            if schema.__name__ in list(config_manager.configurations.keys())
        ]

        to_file(
            header="TODO header",
            schemas=schemas,
            config_values=config_values,
            format="yaml",
            path=output_path,
        )

    def create_template(self, output_path: PathLike):
        to_file(
            header=TEMPLE_HEADER,
            schemas=self.schemas,
            exclusive_groups=self.exclusive_groups,
            format="yaml",
            path=output_path,
        )


config_manager = ConfigManager()
