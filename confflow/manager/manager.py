from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Any, Iterator, List, Union

import yaml

from confflow.config_factory import create_config
from confflow.mixins import IPythonMixin

from ..formatter import format_schema
from ..schema import Schema
from .confflow import Confflow


class Manager(IPythonMixin):
    def __init__(self, *schemas: Schema):
        if not len(schemas):
            raise ValueError("Manager must contain at least one schema")

        self._schemas: OrderedDict[str, Schema] = OrderedDict(
            (schema.name, schema) for schema in schemas
        )

    def template(self, file_path: Union[str, Path], descriptions=False):
        Path(file_path).write_text(
            "\n\n".join(
                [
                    format_schema(schema, descriptions=descriptions)
                    for schema in self._schemas.values()
                ]
            ),
            encoding="utf-8",
        )

    def load(self, file_path: Union[str, Path]) -> Confflow:
        config_path: Path = Path(file_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")

        try:
            with config_path.open("r", encoding="utf-8") as f:
                raw_data: dict[str, Any] = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file {file_path}: {e}") from e

        schema_configs = []
        for schema in self._schemas.values():
            section_data: Any = raw_data.get(schema.name)
            if section_data is None:
                raise ValueError(
                    f"Missing required section '{schema.name}' in config file {file_path}"
                )

            if not isinstance(section_data, dict):
                raise ValueError(
                    f"Section '{schema.name}' must be a dictionary/object, got {type(section_data).__name__}"
                )

            schema_config = create_config(schema, section_data)
            schema_configs.append(schema_config)

        return Confflow(*schema_configs)

    def keys(self) -> Iterator[str]:
        return iter(self._schemas.keys())

    def values(self) -> Iterator[Schema]:
        return iter(self._schemas.values())

    def items(self) -> Iterator[tuple[str, Schema]]:
        return iter(self._schemas.items())

    def __getitem__(self, key: str) -> Schema:
        if key not in self._schemas:
            available_keys: List[str] = list(self._schemas.keys())
            raise KeyError(
                f"Schema '{key}' not found. " f"Available schemas: {available_keys}."
            )
        return self._schemas[key]

    def __contains__(self, key: str) -> bool:
        return key in self._schemas

    def __len__(self) -> int:
        return len(self._schemas)

    def __repr__(self) -> str:
        return f"Manager(schemas={list(self._schemas.keys())})"
