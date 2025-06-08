from pathlib import Path
from typing import Union, get_args

import yaml

from confflow.core.manager.schema.field import Field
from confflow.types import Value

from ..config import Config
from .schema import Schema


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
                f.write(f"# Template for schema: {schema.name}\n")
                f.write(f"{schema.name}:\n")

                for field in schema.fields:
                    py_type = self._get_field_type(field)  # type: ignore
                    yaml_tag: str = self._get_yaml_tag(py_type)

                    default_value = field.default_value  # TODO correct type

                    required_note: str = (
                        "required" if getattr(field, "required", False) else "optional"
                    )

                    constraints_note: str = (
                        f"constraints={field.constraints}" if field.constraints else ""
                    )

                    comment_parts: list[str] = [required_note]

                    if constraints_note:
                        comment_parts.append(constraints_note)
                    if default_value != "":
                        comment_parts.append(f"default={default_value}")

                    comment = "  # " + ", ".join(comment_parts)

                    f.write(f"  {field.name}: {yaml_tag} {default_value}{comment}\n")

                f.write("\n")

    def _get_field_type(self, field: Field[Value]) -> type:
        args = get_args(field.__class__)  # TODO correct type
        if args:
            return args[0]
        return str

    def _get_yaml_tag(self, py_type: type) -> str:
        tag_map: dict[type, str] = {
            str: "!!str",
            int: "!!int",
            float: "!!float",
            bool: "!!bool",
            list: "!!seq",
            dict: "!!map",
        }

        return tag_map.get(py_type, "!!str")

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
                value = section.get(field.name, field.default_value)  # type: ignore | correct

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

    def __getitem__(self, key: str):  # TODO add return type
        return self._configs[key]

    def __contains__(self, key: str):  # TODO add return type
        return key in self._configs

    # Only for iPython # TODO maybe remove here add as mixin or so
    def _ipython_key_completions_(self) -> list[str]:
        return list(self._configs.keys())
