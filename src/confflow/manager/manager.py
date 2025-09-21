from __future__ import annotations

import typing
from collections import OrderedDict
from pathlib import Path

import yaml

from confflow.config_factory import create_config
from confflow.formatter import format_schema
from confflow.mixins import IPythonMixin
from confflow.schema import Schema

from .confflow import Confflow

if typing.TYPE_CHECKING:
    from collections.abc import ItemsView, KeysView, ValuesView

    from confflow.config.config import Config
    from confflow.types import YAMLDocument, YAMLKey, YAMLTypes

    from .group import Group


class Manager(IPythonMixin):
    def __init__(self, *items: Schema | Group) -> None:
        if not items:
            raise ValueError("Manager must contain at least one schema or group")  # noqa: EM101, TRY003

        self._schemas: OrderedDict[str, Schema] = OrderedDict()
        self._groups: list[Group] = []
        self._schema_to_group: dict[str, Group] = {}

        for item in items:
            if isinstance(item, Schema):
                if item.name in self._schemas:
                    raise ValueError(f"Duplicate schema name: {item.name}")  # noqa: EM102, TRY003
                self._schemas[item.name] = item
            else:
                self._groups.append(item)
                for schema in item:
                    if schema.name in self._schemas:
                        raise ValueError(f"Duplicate schema name: {schema.name}")  # noqa: EM102, TRY003
                    self._schemas[schema.name] = schema
                    self._schema_to_group[schema.name] = item

    def template(self, file_path: str | Path, *, descriptions: bool = False) -> None:
        # Add standalone schemas
        standalone_schemas: list[Schema] = [
            schema
            for schema in self._schemas.values()
            if schema.name not in self._schema_to_group
        ]

        sections: list[str] = [
            format_schema(schema, descriptions=descriptions)
            for schema in standalone_schemas
        ]

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

    def load(self, file_path: str | Path) -> Confflow:
        config_path: Path = Path(file_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")  # noqa: EM102, TRY003

        try:
            with config_path.open("r", encoding="utf-8") as f:
                raw_data: YAMLDocument = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file {file_path}: {e}") from e  # noqa: EM102, TRY003

        # Validate groups first
        self._validate_groups(raw_data, file_path)

        schema_configs: list[Config] = []
        processed_schemas: set[str] = set()

        # Process standalone schemas
        schema: Schema
        section_data: dict[YAMLKey, YAMLTypes]
        schema_config: Config
        for schema in self._schemas.values():
            if schema.name in self._schema_to_group:
                continue  # Will be processed with group

            section_data = raw_data[schema.name]

            if not isinstance(section_data, dict):
                raise TypeError(  # noqa: TRY003
                    f"Section '{schema.name}' must be a dictionary/object, got {type(section_data).__name__}",  # noqa: E501, EM102
                )

            schema_config = create_config(schema, section_data)
            schema_configs.append(schema_config)
            processed_schemas.add(schema.name)

        # Process groups - validate and process according to group rules
        for group in self._groups:
            present_schemas: list[str] = [
                schema_name for schema_name in group.names if schema_name in raw_data
            ]

            if not present_schemas:
                raise ValueError(  # noqa: TRY003
                    f"Missing required group section in config file {file_path}. "  # noqa: EM102
                    f"Must include at least one of: {list(group.names)}",
                )

            # Process all present schemas from the group (behavior depends on group type)  # noqa: E501
            for schema_name in present_schemas:
                schema = self._schemas[schema_name]
                section_data = raw_data[schema_name]

                if not isinstance(section_data, dict):
                    raise TypeError(  # noqa: TRY003
                        f"Section '{schema_name}' must be a dictionary/object, got {type(section_data).__name__}",  # noqa: E501, EM102
                    )

                schema_config = create_config(schema, section_data)
                schema_configs.append(schema_config)
                processed_schemas.add(schema_name)

        return Confflow(*schema_configs)

    def _validate_groups(
        self,
        raw_data: YAMLDocument,
        file_path: str | Path,
    ) -> None:
        for group in self._groups:
            present_schemas: list[str] = [
                schema_name for schema_name in group.names if schema_name in raw_data
            ]
            group.validate(present_schemas, file_path)

    def keys(self) -> KeysView[str]:
        return self._schemas.keys()

    def values(self) -> ValuesView[Schema]:
        return self._schemas.values()

    def items(self) -> ItemsView[str, Schema]:
        return self._schemas.items()

    def __getitem__(self, key: str) -> Schema:
        if key not in self._schemas:
            available_keys: list[str] = list(self._schemas.keys())
            raise KeyError(  # noqa: TRY003
                f"Schema '{key}' not found. Available schemas: {available_keys}.",  # noqa: EM102
            )
        return self._schemas[key]

    def __contains__(self, key: str) -> bool:
        return key in self._schemas

    def __len__(self) -> int:
        return len(self._schemas)

    def __repr__(self) -> str:
        items: list[str] = []

        # Add standalone schemas
        standalone: list[str] = [
            name for name in self._schemas if name not in self._schema_to_group
        ]
        if standalone:
            items.extend(standalone)

        # Add groups
        items.extend(
            f"{group.__class__.__name__}({list(group.names)})" for group in self._groups
        )

        return f"Manager({items})"
