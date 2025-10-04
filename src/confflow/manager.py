from __future__ import annotations

import typing
from pathlib import Path

import yaml

from ._config import Config, dict_to_dataclass

if typing.TYPE_CHECKING:
    from confflow._schema import Schema
    from confflow._shared import YamlDict


@typing.final
class Manager:
    """Manages multiple configuration schemas for validation and template generation.

    The Manager class coordinates validation of configuration data against multiple
    schemas and provides functionality to load configurations from files and generate
    template files for each schema.

    Args:
        *schemas: Variable number of Schema objects to manage. At least one schema
            is required and duplicate schemas are not allowed.

    Raises:
        ValueError: If no schemas are provided or if duplicate schemas are detected.

    """

    def __init__(self, *schemas: Schema) -> None:
        if not schemas:
            raise ValueError("At least one schema is required")  # noqa: EM101, TRY003

        if len(schemas) != len(set(schemas)):
            raise ValueError("Duplicate schemas are not allowed")  # noqa: EM101, TRY003

        self._schemas: dict[str, Schema] = {schema.name: schema for schema in schemas}

    def validate(self, data: YamlDict, /) -> None:
        """Validate configuration data against all registered schemas.

        Checks that all keys in the data correspond to valid schema names and that
        the data for each schema passes its validation rules.

        Args:
            data: Dictionary containing configuration data to validate, where keys
                are schema names and values are the configuration for that schema.

        Raises:
            ValueError: If invalid keys are found that don't match any schema names,
                or if the data fails schema validation.

        """
        names: set[str] = set(self._schemas.keys())
        keys: set[str] = set(data.keys())

        if invalid := keys - names:
            raise ValueError(  # noqa: TRY003
                f"Invalid keys found: {sorted(invalid)}. "  # noqa: EM102
                f"Valid schema names are: {sorted(names)}",
            )

        for key in data:
            self._schemas[key].validate(data[key])  # type: ignore  # noqa: PGH003

    def loads(self, data: YamlDict) -> Config:
        """Load and validate configuration data from a dictionary.

        Validates the provided data against all schemas and converts it to a
        frozen dataclass Config object.

        Args:
            data: Dictionary containing configuration data to load.

        Returns:
            Config: A frozen dataclass containing the validated configuration.

        Raises:
            ValueError: If the data fails validation.

        """
        self.validate(data)

        return dict_to_dataclass(name="Config", data=data, frozen=True)

    def create_templates(self, directory: str | Path, /) -> None:
        """Create individual template YAML files for each schema in a directory.

        Generates a separate {schemaname}_template.yml file for each registered
        schema. Creates the target directory if it doesn't exist.

        Args:
            directory: Path to the directory where template files will be created.
                The directory will be created (including parent directories) if it
                doesn't exist.

        """
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)

        for schema in self._schemas.values():
            template_path = dir_path / f"{schema.name}_template.yml"
            template_path.write_text(
                schema.to_formatted_string() + "\n",
                encoding="utf-8",
            )

    def load(
        self,
        *filepaths: str | Path,
    ) -> Config:
        """Load and merge configuration from multiple YAML files.

        Reads YAML data from one or more file paths, merges them into a single
        configuration, validates against schemas, and returns a Config object.
        If multiple files contain the same keys, later files override earlier ones.

        If a single argument is provided and it's a directory, all files ending
        with .yml in that directory will be loaded (non-recursively).

        Args:
            *filepaths: One or more file paths (str or Path) to load configuration
                from. If a single directory path is provided, all .yml files in
                that directory are loaded.

        Returns:
            Config: A frozen dataclass containing the validated merged configuration.

        Raises:
            ValueError: If no filepaths are provided, or if the merged data fails
                validation.
            FileNotFoundError: If any specified file path doesn't exist.
            yaml.YAMLError: If any file contains invalid YAML.

        """
        if not filepaths:
            raise ValueError("At least one filepath is required")  # noqa: EM101, TRY003

        paths_to_load: list[str | Path] = list(filepaths)

        if len(filepaths) == 1:
            path = Path(filepaths[0])
            if path.is_dir():
                # Load all .yml files from directory
                paths_to_load = sorted(path.glob("*.yml"))
                if not paths_to_load:
                    raise ValueError(f"No .yml files found in directory: {path}")  # noqa: EM102, TRY003

        merged_data: YamlDict = {}

        for filepath in paths_to_load:
            data = yaml.safe_load(
                Path(filepath).read_text(encoding="utf-8"),
            )

            if data:
                merged_data.update(data)

        return self.loads(merged_data) if merged_data else self.loads({})
