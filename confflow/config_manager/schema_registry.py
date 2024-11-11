from typing import List, OrderedDict, Type

from pydantic import BaseModel as BaseConfig


class SchemaRegistry:
    def __init__(self):
        self._schema_map: OrderedDict[str, Type[BaseConfig]] = OrderedDict()

    def register_schemas(self, *config_classes: Type[BaseConfig]):
        for config_classe in config_classes:
            if not issubclass(config_classe, BaseConfig):
                raise TypeError(f"{config_classe} must be a subclass of BaseModel.")

            config_name: str = config_classe.__name__
            if config_name in self._schema_map:
                raise ValueError(f"Schema '{config_name}' is already registered.")

            self._schema_map[config_name] = config_classe

    def get(self, config_name: str) -> Type[BaseConfig]:
        if config_name not in self._schema_map:
            raise KeyError(f"Schema '{config_name}' is not registered.")
        return self._schema_map[config_name]

    def values(self) -> List[Type[BaseConfig]]:
        return list(self._schema_map.values())

    def __getitem__(self, config_name: str) -> Type[BaseConfig]:
        return self.get(config_name)

    def __contains__(self, config_name: str) -> bool:
        return config_name in self._schema_map
