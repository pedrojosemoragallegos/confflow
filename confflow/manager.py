from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple, Union

import yaml

from confflow.mixins import IPythonMixin

from .config_proxy import ConfigProxy
from .core import Config, Schema
from .formatter import format_schema


class Manager(IPythonMixin):
    def __init__(self, *schemas: Schema):
        self._schemas: Tuple[Schema, ...] = schemas
        self._configs: Dict[str, Config] = {}

    @property
    def schemas(self) -> Tuple[Schema, ...]:
        return self._schemas

    def build(self, file_path: Union[str, Path]) -> Manager:
        formatted_schemas: List[str] = [
            format_schema(schema) for schema in self._schemas
        ]
        Path(file_path).write_text("\n\n".join(formatted_schemas), encoding="utf-8")
        return self

    def load(self, file_path: Union[str, Path]) -> ConfigProxy:
        path: Path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")

        try:
            with path.open("r", encoding="utf-8") as f:
                raw_data: Dict[str, Any] = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file {file_path}: {e}") from e

        self._configs.clear()

        for schema in self._schemas:
            section_data: Any = raw_data.get(schema.name)
            if section_data is None:
                raise ValueError(
                    f"Missing required section '{schema.name}' in config file {file_path}"
                )

            if not isinstance(section_data, dict):
                raise ValueError(
                    f"Section '{schema.name}' must be a dictionary/object, got {type(section_data).__name__}"
                )

            config: Config = self._create_config_from_schema(schema, section_data)
            self._configs[schema.name] = config

        return ConfigProxy(self)

    def is_loaded(self) -> bool:
        return len(self._configs) > 0

    def _create_config_from_schema(
        self, schema: Schema, section_data: Dict[str, Any]
    ) -> Config:
        config: Config = Config(name=schema.name, description=schema.description)
        self._process_schema(schema, section_data, config)
        return config

    def _process_schema(
        self, schema_obj: Schema, data: Dict[str, Any], config: Config
    ) -> None:
        from .core import Config

        for key, field_or_subschema in schema_obj.items():
            if isinstance(field_or_subschema, Schema):
                nested_data: Any = data.get(key)
                if nested_data is None:
                    raise ValueError(
                        f"Missing required subschema section '{key}' in '{schema_obj.name}'"
                    )

                if not isinstance(nested_data, dict):
                    raise ValueError(
                        f"Subschema '{key}' in '{schema_obj.name}' must be a dictionary/object, "
                        f"got {type(nested_data).__name__}"
                    )

                nested_config: Config = Config(
                    name=key, description=field_or_subschema.description
                )
                self._process_schema(field_or_subschema, nested_data, nested_config)
                config.SubConfig(key, nested_config)
            else:
                value: Any = data.get(key, field_or_subschema.default_value)
                if value is None and field_or_subschema.required:
                    raise ValueError(
                        f"Missing required field '{key}' in section '{schema_obj.name}'"
                    )

                try:
                    config.Entry(
                        value=value,
                        name=key,
                        description=field_or_subschema.description,
                        default_value=field_or_subschema.default_value,
                        required=field_or_subschema.required,
                        constraints=field_or_subschema.constraints,
                    )
                except Exception as e:
                    raise ValueError(
                        f"Validation failed for field '{key}' in section '{schema_obj.name}': {e}"
                    ) from e

    def keys(self) -> Iterator[str]:
        return self._configs.keys()

    def values(self) -> Iterator[Config]:
        return self._configs.values()

    def items(self) -> Iterator[Tuple[str, Config]]:
        return self._configs.items()

    def __getitem__(self, key: str) -> Config:
        if key not in self._configs:
            available_keys: List[str] = list(self._configs.keys())
            raise KeyError(
                f"Configuration section '{key}' not loaded. "
                f"Available sections: {available_keys}. "
                f"Make sure to call load() first."
            )
        return self._configs[key]

    def __contains__(self, key: str) -> bool:
        return key in self._configs

    def __len__(self) -> int:
        return len(self._configs)

    def __repr__(self) -> str:
        return f"Manager(schemas={[schema.name for schema in self._schemas] if self._schemas else []})"

    def __bool__(self) -> bool:
        return len(self._configs) > 0
