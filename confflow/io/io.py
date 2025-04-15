from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Set, Type

import yaml
from pydantic import BaseModel

from ..common.types import ParsedData, PathLike, SchemaGroup
from ..core.registry.schema_registry import SchemaRegistry
from .formatter import YAMLFormatter
from .formatter.base_formatter import BaseFormatter

OutputFormat = Literal["yaml"]

FORMATTER_MAP: Dict[OutputFormat, Type[BaseFormatter]] = {"yaml": YAMLFormatter}


def to_file(
    schemas: List[BaseModel],
    format: OutputFormat,
    path: PathLike,
    header: Optional[List[str]] = None,
    exclusive_groups: Optional[List[SchemaGroup]] = None,
    defaults: Optional[Dict[Type[BaseModel], Dict[str, Any]]] = None,
) -> None:
    path: Path = Path(path)
    formatter_cls: Optional[Type[BaseFormatter]] = FORMATTER_MAP.get(format)

    if formatter_cls is None:
        raise ValueError(f"Unsupported format: {format}")

    if exclusive_groups is None:
        exclusive_groups = []

    content: str = formatter_cls.generate(
        schemas,
        header=header,
        exclusive_groups=exclusive_groups,
        defaults=defaults,
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def load_configuration(
    input_path: PathLike,
    mutually_exclusive_groups: List[List[Type[BaseModel]]],
    configurations: OrderedDict[str, BaseModel],
    schema_registry: SchemaRegistry,
) -> None:
    input_path = Path(input_path)

    with open(input_path, "r", encoding="utf-8") as f:
        parsed_data: ParsedData = yaml.safe_load(f)

    loaded_config_names: Set[str] = set(parsed_data.keys())

    for group in mutually_exclusive_groups:
        group_names = [cls.__name__ for cls in group]
        active_configs = [name for name in group_names if name in loaded_config_names]

        if len(active_configs) > 1:
            raise ValueError(
                f"Mutually exclusive conflict: Multiple configurations from the group {group_names} are loaded: {active_configs}"
            )

    for config_name, config_data in parsed_data.items():
        config_class = schema_registry.get(config_name)
        if not config_class:
            raise ValueError(f"Unknown config type: {config_name}")

        configurations[config_name] = config_class(**config_data)
