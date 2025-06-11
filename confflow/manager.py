from pathlib import Path
from typing import Union

import yaml

from .core.config import Config
from .core.schema import Schema
from .formatter import format_schema


class Manager:
    def __init__(self, *schema: Schema):
        self._schemas: tuple[Schema, ...] = schema
        self._configs: dict[str, Config] = {}

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
            raw_data = yaml.safe_load(f) or {}

        for schema in self._schemas:
            section_data = raw_data.get(schema.name)
            if section_data is None:
                raise ValueError(f"Missing required section '{schema.name}' in config")

            config = Config(name=schema.name, description=schema.description)

            def process_fields(schema_obj: Schema, data: dict, parent_key: str = ""):
                for key, field_or_subschema in schema_obj.items():
                    full_key = f"{parent_key}.{key}" if parent_key else key

                    if isinstance(field_or_subschema, Schema):
                        nested_data = data.get(key)
                        if nested_data is None:
                            raise ValueError(
                                f"Missing required subschema section '{full_key}'"
                            )

                        process_fields(field_or_subschema, nested_data, full_key)
                    else:
                        value = data.get(key, field_or_subschema.default_value)

                        if value is None and field_or_subschema.required:
                            raise ValueError(f"Missing required field '{full_key}'")

                        config.addField(
                            value=value,
                            name=full_key,
                            description=field_or_subschema.description,
                            default_value=field_or_subschema.default_value,
                            required=field_or_subschema.required,
                            constraints=field_or_subschema.constraints,
                        )

            process_fields(schema, section_data)

            self._configs[schema.name] = config

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
