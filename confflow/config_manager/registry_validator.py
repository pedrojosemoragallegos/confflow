from typing import List, Type

from pydantic import BaseModel as BaseConfig

from .schema_registry import SchemaRegistry


def is_registered_config_name(
    schema_registry: SchemaRegistry, config_name: str
) -> bool:
    return config_name in schema_registry


def is_registered_config_class(
    config_class: Type[BaseConfig], schema_registry: SchemaRegistry
) -> bool:
    return config_class in schema_registry.values()


def validate_config_classes(
    schema_registry: SchemaRegistry, *config_classes: Type[BaseConfig]
):
    invalid_config_classes: List[Type[BaseConfig]] = [
        config_class
        for config_class in config_classes
        if not is_registered_config_class(
            schema_registry=schema_registry, config_class=config_class
        )
    ]

    if invalid_config_classes:
        raise ValueError(
            f"The following classes are not valid: {', '.join(invalid_config_classes)}"
        )
