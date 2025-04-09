import json
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeAlias

import yaml
from pydantic import BaseModel

from ..io import to_file
from ..utils.types import PathLike, SchemaGroup, SchemaName, SchemaType
from .exclusive_schema_manager import ExclusiveSchemaManager
from .schema_registry import SchemaRegistry

ConfigurationMap: TypeAlias = Dict[SchemaName, BaseModel]
DefaultsMap: TypeAlias = Dict[SchemaType, Dict[str, Any]]

TEMPLATE_HEADER: List[str] = [
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
            self._data: ConfigurationMap = {}
            ConfigManager._initialized = True

    def register_schema(
        self,
        schema: SchemaType,
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
            name: SchemaName = instance.__class__.__name__
            if name not in self._schema_registry:
                raise ValueError(f"Schema '{name}' is not registered.")
            self._data[name] = instance
        self._exclusivity_manager.validate(list(self._data.values()))

    def __getitem__(self, key: str) -> BaseModel:
        return self._data[key].model_dump()

    def __setitem__(self, key: str, value: BaseModel) -> None:
        if key not in self._schema_registry:
            raise ValueError(f"Schema '{key}' is not registered.")
        self._data[key] = value
        self._exclusivity_manager.validate(list(self._data.values()))

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self) -> str:
        return json.dumps(self.as_dict(), indent=2)

    def __str__(self) -> str:
        return str(self.as_dict())

    def keys(self):
        return self._data.keys()

    def values(self):
        return (v.model_dump() for v in self._data.values())

    def items(self):
        return ((k, v.model_dump()) for k, v in self._data.items())

    def as_dict(self) -> Dict[str, Any]:
        return {k: v.model_dump() for k, v in self._data.items()}

    @property
    def schemas(self) -> List[SchemaType]:
        return self._schema_registry.schemas

    @property
    def exclusive_groups(self) -> List[SchemaGroup]:
        return self._exclusivity_manager.exclusive_groups

    def save(self, output_path: PathLike) -> None:
        output_path: Path = Path(output_path)
        if not self._data:
            raise ValueError("No configurations to save.")
        defaults: DefaultsMap = {
            type(config): config.model_dump() for config in self._data.values()
        }
        to_file(
            schemas=list(self._data.values()),
            format="yaml",
            path=output_path,
            header=["Generated configuration file"],
            defaults=defaults,
        )

    def create_template(self, output_path: PathLike) -> None:
        to_file(
            header=TEMPLATE_HEADER,
            schemas=self.schemas,
            exclusive_groups=self.exclusive_groups,
            format="yaml",
            path=output_path,
        )

    def load(self, input_path: PathLike) -> None:
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {input_path}")

        with open(input_path, "r", encoding="utf-8") as f:
            parsed_data: Dict[str, Any] = yaml.safe_load(f) or {}

        loaded_configurations: ConfigurationMap = {}
        loaded_names = set(parsed_data.keys())

        exclusive_names = {
            schema.__name__ for group in self.exclusive_groups for schema in group
        }

        required_names = {
            schema.__name__
            for schema in self._schema_registry.schemas
            if schema.__name__ not in exclusive_names
        }

        missing_required = required_names - loaded_names
        if missing_required:
            raise ValueError(
                f"Missing configuration(s) for required schema(s): {sorted(missing_required)}"
            )

        for group in self.exclusive_groups:
            group_names = {schema.__name__ for schema in group}
            present = group_names & loaded_names
            if len(present) == 0:
                raise ValueError(
                    f"No configuration provided for mutually exclusive group: {sorted(group_names)}"
                )
            if len(present) > 1:
                raise ValueError(
                    f"Multiple configurations provided for mutually exclusive group {sorted(group_names)}: {sorted(present)}"
                )

        for schema_name, config_data in parsed_data.items():
            schema_class = self._schema_registry[schema_name]
            if not schema_class:
                raise ValueError(f"Unknown schema type: '{schema_name}'")
            loaded_configurations[schema_name] = schema_class(**config_data)

        self._data = loaded_configurations


config_manager = ConfigManager()
