from typing import List

from ..utils.types import BaseConfig, ConfigName, SchemaMap


class SchemaRegistry:
    """
    Manages the registration and retrieval of configuration schemas.

    This registry allows adding new schema configurations and retrieving
    them by their names. It ensures each schema is uniquely identifiable
    by its name.
    """

    def __init__(self):
        self._schema_map: SchemaMap = SchemaMap()

    def register_schemas(self, *configs: BaseConfig):
        for config in configs:
            config_name: ConfigName = config.__name__

            if config_name in self._schema_map:
                raise ValueError(f"Schema '{config_name}' is already registered.")

            self._schema_map[config_name] = config

    def get(self, config_name: ConfigName) -> BaseConfig:
        if config_name not in self._schema_map:
            raise KeyError(f"Schema '{config_name}' is not registered.")

        return self._schema_map[config_name]

    def values(self) -> List[BaseConfig]:
        return list(self._schema_map.values())

    def __getitem__(self, config_name: ConfigName) -> BaseConfig:
        return self.get(config_name)

    def __contains__(self, config_name: ConfigName) -> bool:
        return config_name in self._schema_map
