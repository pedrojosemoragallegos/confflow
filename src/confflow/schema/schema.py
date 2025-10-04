from __future__ import annotations

import re
import typing

import typing_extensions

from confflow.mixins import FormattedStringMixin
from confflow.shared import yaml_indent

from .groups.group import Group

if typing.TYPE_CHECKING:
    from confflow.schema.fields import (
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
    from confflow.shared import YamlDict


@typing.final
class Schema(FormattedStringMixin):
    SAFE_YAML_KEY = re.compile(r"^(?!-)(?!\d)[A-Za-z_][A-Za-z0-9_-]*$")

    def __init__(self, name: str, /, description: str | None = None) -> None:
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
        return self._name

    @property
    def description(self) -> str | None:
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
        if (field.name in self._mapping) or (field.name in self._field_names):
            raise ValueError(f"Field '{field.name}' already exists")  # noqa: EM102, TRY003

        self._mapping[field.name] = field
        self._field_names.add(field.name)
        self._nodes.append(field)

        return self

    def __add_schema(self, schema: Schema, /) -> typing_extensions.Self:
        if (schema.name in self._mapping) or (schema.name in self._schema_names):
            raise ValueError(f"Schema '{schema.name}' already exists")  # noqa: EM102, TRY003

        self._mapping[schema.name] = schema
        self._schema_names.add(schema.name)
        self._nodes.append(schema)

        return self

    def __add_group(self, group: Group) -> typing_extensions.Self:
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
        if isinstance(item, Schema):
            return self.__add_schema(item)

        if isinstance(item, Group):
            return self.__add_group(item)

        return self.__add_field(item)

    def validate(self, data: YamlDict, /) -> None:
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
        return (
            yaml_indent * indent
            + f"{self.name}:\n"
            + "\n".join(
                [node.to_formatted_string(indent + 1) for node in self._nodes],
            )
        )

    def __repr__(self) -> str:
        return (
            "Schema("
            f"name={self.name!r}"
            f"description={self.description!r}"
            f"groups={' ,'.join([repr(group) for group in self._groups])}"
            f"entries={' ,'.join([repr(entry) for entry in self._mapping.values()])}"
            ")"
        )
