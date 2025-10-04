from __future__ import annotations

import re
import typing

import typing_extensions

from confflow._mixins import FormattedStringMixin
from confflow._shared import yaml_indent

from .groups.group import Group

if typing.TYPE_CHECKING:
    from confflow._schema.fields import (
        BooleanField,
        Booleanlist,
        BytesField,
        Byteslist,
        DateField,
        Datelist,
        FloatField,
        Floatlist,
        IntegerField,
        Integerlist,
        StringField,
        Stringlist,
    )
    from confflow._shared import YamlDict


@typing.final
class Schema(FormattedStringMixin):
    """A schema definition for validating and formatting YAML configuration structures.

    The Schema class provides a way to define hierarchical configuration structures
    with fields, nested schemas, and validation groups. It ensures that configuration
    keys follow YAML-safe naming conventions and provides validation and formatting
    capabilities.

    Attributes:
        SAFE_YAML_KEY: A compiled regex pattern that validates YAML-safe key names.
            Keys must start with a letter or underscore, not with a hyphen or digit,
            and may only contain letters, digits, underscores, or hyphens.

    """

    SAFE_YAML_KEY = re.compile(r"^(?!-)(?!\d)[A-Za-z_][A-Za-z0-9_-]*$")

    def __init__(self, name: str, /, description: str | None = None) -> None:
        """Initialize a new Schema instance.

        Args:
            name: The name of the schema. Must be a valid YAML key (start with letter
                or underscore, contain only letters, digits, underscores, or hyphens).
            description: A description of the schema's purpose. Must not be empty.

        Raises:
            ValueError: If the name doesn't match YAML key requirements or if the
                description is empty.

        """
        if not Schema.SAFE_YAML_KEY.fullmatch(name):
            raise ValueError(  # noqa: TRY003
                f"Invalid YAML key name: {name!r}. "  # noqa: EM102
                "Must start with a letter or '_', not with '-' or digit, "
                "and may only contain letters, digits, underscores, or hyphens.",
            )

        if not description:
            raise ValueError("`description` should not be empty")  # noqa: EM101, TRY003

        self._name: str = name
        self._description: str | None = description
        self._mapping: dict[
            str,
            Schema
            | BooleanField
            | Booleanlist
            | BytesField
            | Byteslist
            | DateField
            | Datelist
            | FloatField
            | Floatlist
            | IntegerField
            | Integerlist
            | StringField
            | Stringlist,
        ] = {}
        self._nodes: list[
            Schema
            | Group
            | BooleanField
            | Booleanlist
            | BytesField
            | Byteslist
            | DateField
            | Datelist
            | FloatField
            | Floatlist
            | IntegerField
            | Integerlist
            | StringField
            | Stringlist,
        ] = []
        self._schema_names: set[str] = set()
        self._field_names: set[str] = set()
        self._groups: set[Group] = set()

    @property
    def name(self) -> str:
        """Get the schema name.

        Returns:
            The name of the schema.

        """
        return self._name

    @property
    def description(self) -> str | None:
        """Get the schema description.

        Returns:
            The description of the schema, or None if not set.

        """
        return self._description

    def __add_field(
        self,
        field: BooleanField
        | Booleanlist
        | BytesField
        | Byteslist
        | DateField
        | Datelist
        | FloatField
        | Floatlist
        | IntegerField
        | Integerlist
        | StringField
        | Stringlist,
        /,
    ) -> typing_extensions.Self:
        """Add a field to the schema.

        Args:
            field: The field instance to add to the schema.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If a field with the same name already exists.

        """
        if (field.name in self._mapping) or (field.name in self._field_names):
            raise ValueError(f"Field '{field.name}' already exists")  # noqa: EM102, TRY003

        self._mapping[field.name] = field
        self._field_names.add(field.name)
        self._nodes.append(field)

        return self

    def __add_schema(self, schema: Schema, /) -> typing_extensions.Self:
        """Add a nested schema to this schema.

        Args:
            schema: The schema instance to add as a nested schema.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If a schema with the same name already exists.

        """
        if (schema.name in self._mapping) or (schema.name in self._schema_names):
            raise ValueError(f"Schema '{schema.name}' already exists")  # noqa: EM102, TRY003

        self._mapping[schema.name] = schema
        self._schema_names.add(schema.name)
        self._nodes.append(schema)

        return self

    def __add_group(self, group: Group) -> typing_extensions.Self:
        """Add a validation group to the schema.

        A group contains multiple schemas with validation rules that apply across them.

        Args:
            group: The group instance to add to the schema.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If the group already exists or if any schema in the group
                has a name that conflicts with existing schemas.

        """
        if group in self._groups:
            raise ValueError("Group already exists in schema")  # noqa: EM101, TRY003

        for schema in group.schemas:
            if (schema.name in self._mapping) or (schema.name in self._schema_names):
                raise ValueError(f"Schema '{schema.name}' from group already exists")  # noqa: EM102, TRY003

        self._mapping.update({schema.name: schema for schema in group.schemas})
        self._schema_names.update([schema.name for schema in group.schemas])
        self._groups.add(group)
        self._nodes.append(group)

        return self

    @typing.overload
    def add(self, schema: Schema, /) -> typing_extensions.Self: ...
    @typing.overload
    def add(
        self,
        field: BooleanField
        | Booleanlist
        | BytesField
        | Byteslist
        | DateField
        | Datelist
        | FloatField
        | Floatlist
        | IntegerField
        | Integerlist
        | StringField
        | Stringlist,
        /,
    ) -> typing_extensions.Self: ...
    @typing.overload
    def add(self, group: Group, /) -> typing_extensions.Self: ...
    def add(
        self,
        item: Schema
        | Group
        | BooleanField
        | Booleanlist
        | BytesField
        | Byteslist
        | DateField
        | Datelist
        | FloatField
        | Floatlist
        | IntegerField
        | Integerlist
        | StringField
        | Stringlist,
        /,
    ) -> typing_extensions.Self:
        """Add a schema, field, or group to this schema.

        This method dispatches to the appropriate private method based on the type
        of the item being added.

        Args:
            item: The schema, field, or group to add. Can be:
                - A nested Schema instance
                - A Group instance containing multiple schemas
                - Any field type (BooleanField, IntegerField, StringField, etc.)

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If an item with the same name already exists, or if a group
                contains schemas with conflicting names.

        """
        if isinstance(item, Schema):
            return self.__add_schema(item)

        if isinstance(item, Group):
            return self.__add_group(item)

        return self.__add_field(item)

    def validate(self, data: YamlDict, /) -> None:
        """Validate data against this schema.

        Validates the provided data dictionary by:
        1. Running validation for all groups (which may have cross-field constraints)
        2. Validating each key-value pair against its corresponding schema or field

        Args:
            data: A dictionary containing the data to validate, typically loaded
                from a YAML file.

        Raises:
            ValidationError: If the data doesn't conform to the schema constraints.
            KeyError: If required fields are missing or unknown fields are present.

        """
        for group in self._groups:
            group(*data.keys())

        for key, value in data.items():
            schema_or_field: (
                Schema
                | BooleanField
                | Booleanlist
                | BytesField
                | Byteslist
                | DateField
                | Datelist
                | FloatField
                | Floatlist
                | IntegerField
                | Integerlist
                | StringField
                | Stringlist
            ) = self._mapping[key]

            schema_or_field.validate(value)  # type: ignore  # noqa: PGH003

    def to_formatted_string(self, indent: int = 0) -> str:
        """Convert the schema to a formatted string representation.

        Generates a human-readable, indented string showing the schema structure
        with all nested schemas and fields.

        Args:
            indent: The indentation level for this schema (used for nested schemas).
                Defaults to 0.

        Returns:
            A formatted string representation of the schema with proper indentation.

        """
        return (
            yaml_indent * indent
            + f"# {self.description}\n"
            + yaml_indent * indent
            + f"{self.name}:\n"
            + "\n".join(
                [node.to_formatted_string(indent + 1) for node in self._nodes],
            )
        )

    def __repr__(self) -> str:
        """Return a string representation of the Schema instance.

        Returns:
            A string containing the schema's name, description, groups, and entries.

        """
        return (
            "Schema("
            f"name={self.name!r}"
            f"description={self.description!r}"
            f"groups={' ,'.join([repr(group) for group in self._groups])}"
            f"entries={' ,'.join([repr(entry) for entry in self._mapping.values()])}"
            ")"
        )
