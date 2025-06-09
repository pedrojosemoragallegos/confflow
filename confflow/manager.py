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

    # TODO move logic outside of class
    def create_template(self, file_path: Union[str, Path]):
        with Path(file_path).open("w", encoding="utf-8") as f:
            for schema in self._schemas:
                f.write(format_schema(schema=schema))

    # TODO move logic outside of class
    def load(self, file_path: Union[str, Path]):
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")

        with path.open("r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f) or {}  # type: ignore

        for schema in self._schemas:
            section = raw_data.get(schema.name, {})  # type: ignore | correct
            config = Config(name=schema.name, description=schema.description)
            for field in schema.fields:
                value = section.get(field.name)  # type: ignore | correct

                if value is None and field.required:
                    raise ValueError(
                        f"Missing required field '{field.name}' in section '{schema.name}'"
                    )

                config.addField(
                    value=value,  # type: ignore | correct
                    name=field.name,
                    description=field.description,
                    default_value=field.default_value,  # type: ignore | correct
                    required=field.required,
                    constraints=field.constraints,  # type: ignore | correct
                )

            self._configs[schema.name] = config

    def keys(self):  # TODO add return type
        return self._configs.keys()

    def values(self):  # TODO add return type
        return self._configs.values()

    def items(self):  # TODO add return type
        return self._configs.items()

    def __getitem__(self, key: str) -> Config:  # TODO add return type
        return self._configs[key]

    def __contains__(self, key: str):  # TODO add return type
        return key in self._configs

    # Only for iPython # TODO maybe remove here add as mixin or so
    def _ipython_key_completions_(self) -> list[str]:
        return list(self._configs.keys())
