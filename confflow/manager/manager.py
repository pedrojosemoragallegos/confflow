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
from .group import Group


class Manager(IPythonMixin):
    def __init__(self, *items: Union[Schema, Group]):
        if not items:
            raise ValueError("Manager must contain at least one schema or group")

        self._schemas: OrderedDict[str, Schema] = OrderedDict()
        self._groups: list[Group] = []
        self._schema_to_group: dict[str, Group] = {}

        for item in items:
            if isinstance(item, Schema):
                if item.name in self._schemas:
                    raise ValueError(f"Duplicate schema name: {item.name}")
                self._schemas[item.name] = item
            elif isinstance(item, Group):
                self._groups.append(item)
                for schema in item:
                    if schema.name in self._schemas:
                        raise ValueError(f"Duplicate schema name: {schema.name}")
                    self._schemas[schema.name] = schema
                    self._schema_to_group[schema.name] = item
            else:
                raise TypeError(f"Expected Schema or Group, got {type(item).__name__}")

    def template(self, file_path: Union[str, Path], descriptions=False):
        sections: list[str] = []

        # Add standalone schemas
        standalone_schemas: list[Schema] = [
            schema
            for schema in self._schemas.values()
            if schema.name not in self._schema_to_group
        ]
        for schema in standalone_schemas:
            sections.append(format_schema(schema, descriptions=descriptions))

        # Add grouped schemas with comments
        for group in self._groups:
            sections.append(group.template_comment)

            for i, schema in enumerate(group):
                if i > 0:
                    sections.append("# ┌─── OR ───┐")
                sections.append(format_schema(schema, descriptions=descriptions))

            sections.append("")  # Empty line after group

        Path(file_path).write_text(
            "\n\n".join(sections),
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

        # Validate groups first
        self._validate_groups(raw_data, file_path)

        schema_configs: list[Any] = []
        processed_schemas: set[str] = set()

        # Process standalone schemas
        for schema in self._schemas.values():
            if schema.name in self._schema_to_group:
                continue  # Will be processed with group

            section_data: Any = raw_data.get(schema.name)
            if section_data is None:
                raise ValueError(
                    f"Missing required section '{schema.name}' in config file {file_path}"
                )
            if not isinstance(section_data, dict):
                raise ValueError(
                    f"Section '{schema.name}' must be a dictionary/object, got {type(section_data).__name__}"
                )

            schema_config: Any = create_config(schema, section_data)
            schema_configs.append(schema_config)
            processed_schemas.add(schema.name)

        # Process groups - validate and process according to group rules
        for group in self._groups:
            present_schemas: list[str] = [
                schema_name for schema_name in group.names if schema_name in raw_data
            ]

            if not present_schemas:
                group_names: list[str] = list(group.names)
                raise ValueError(
                    f"Missing required group section in config file {file_path}. "
                    f"Must include at least one of: {group_names}"
                )

            # Process all present schemas from the group (behavior depends on group type)
            for schema_name in present_schemas:
                schema: Schema = self._schemas[schema_name]
                section_data: Any = raw_data[schema_name]

                if not isinstance(section_data, dict):
                    raise ValueError(
                        f"Section '{schema_name}' must be a dictionary/object, got {type(section_data).__name__}"
                    )

                schema_config: Any = create_config(schema, section_data)
                schema_configs.append(schema_config)
                processed_schemas.add(schema_name)

        return Confflow(*schema_configs)

    def _validate_groups(self, raw_data: dict[str, Any], file_path: Union[str, Path]):
        for group in self._groups:
            present_schemas: list[str] = [
                schema_name for schema_name in group.names if schema_name in raw_data
            ]
            group.validate(present_schemas, file_path)

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
        items = []

        # Add standalone schemas
        standalone: list[str] = [
            name for name in self._schemas.keys() if name not in self._schema_to_group
        ]
        if standalone:
            items.extend(standalone)

        # Add groups
        for group in self._groups:
            items.append(f"{group.__class__.__name__}({list(group.names)})")

        return f"Manager({items})"
