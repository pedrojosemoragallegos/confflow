from pathlib import Path
from typing import Any, Union

import yaml

from .core import Config, Schema
from .formatter import format_schema


class Manager:
    def __init__(self, *schema: Schema):
        self._schemas: tuple[Schema, ...] = schema
        self._configs: dict[str, Config] = {}  # TODO dict or orderedict?

    @property
    def schemas(self) -> tuple[Schema, ...]:
        return self._schemas

    def create_template(self, file_path: Union[str, Path]):
        Path(file_path).write_text(
            "\n\n".join([format_schema(schema) for schema in self._schemas])
        )

    def load(self, file_path: Union[str, Path]):
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")

        with path.open("r", encoding="utf-8") as f:
            raw_data: dict[str, Any] = yaml.safe_load(f) or {}  # TODO add typing

        for schema in self._schemas:
            section_data = raw_data.get(schema.name)
            if section_data is None:
                raise ValueError(f"Missing required section '{schema.name}' in config")

            config = Config(name=schema.name, description=schema.description)

            self._process_schema(schema, section_data, config)  # TODO review

            self._configs[schema.name] = config

    def _process_schema(
        self, schema_obj: Schema, data: dict, config: Config
    ):  # TODO add typing
        for key, field_or_subschema in schema_obj.items():
            if isinstance(field_or_subschema, Schema):
                nested_data = data.get(key)
                if nested_data is None:
                    raise ValueError(f"Missing required subschema section '{key}'")

                nested_config = Config(
                    name=key, description=field_or_subschema.description
                )
                self._process_schema(field_or_subschema, nested_data, nested_config)
                config.addSubconfig(key, nested_config)

            else:
                value = data.get(key, field_or_subschema.default_value)
                if value is None and field_or_subschema.required:
                    raise ValueError(f"Missing required field '{key}'")

                config.addField(
                    value=value,
                    name=key,
                    description=field_or_subschema.description,
                    default_value=field_or_subschema.default_value,
                    required=field_or_subschema.required,
                    constraints=field_or_subschema.constraints,
                )

    def keys(self):  # TODO add return type
        return self._configs.keys()

    def values(self):  # TODO add return type
        return self._configs.values()

    def items(self):  # TODO add return type
        return self._configs.items()

    def __getitem__(self, key: str) -> Config:
        return self._configs[key]  # TODO don't return the config itself but a view

    def __contains__(self, key: str):  # TODO add return type
        return key in self._configs

    # Only for iPython # TODO maybe remove here add as mixin or so
    def _ipython_key_completions_(self) -> list[str]:
        return list(self._configs.keys())
