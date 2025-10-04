from __future__ import annotations

import typing
from abc import abstractmethod

import typing_extensions

from confflow.mixins import FormattedStringMixin
from confflow.shared import create_frame, yaml_indent

if typing.TYPE_CHECKING:
    from confflow.schema import Schema


## Base Group
class Group(FormattedStringMixin):
    def __init__(self, *schemas: Schema) -> None:
        self._schemas: frozenset[Schema] = frozenset(schemas)

    @property
    def schemas(self) -> frozenset[Schema]:
        return self._schemas

    def __hash__(self) -> int:
        return hash(self._schemas)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Group):
            return NotImplemented

        return self._schemas == other._schemas

    @abstractmethod
    def __call__(self, *schemas: str) -> None: ...

    @abstractmethod
    def __repr__(self) -> str: ...


## Groups
@typing.final
class OneOf(Group):
    @typing_extensions.override
    def __call__(self, *schemas: str) -> None:
        if (
            matches := sum(1 for schema in self._schemas if schema.name in schemas)
        ) != 1:
            raise ValueError(  # noqa: TRY003
                f"Expected exactly one of {', '.join([repr(schema) for schema in self._schemas])}, but found {matches} matches",  # noqa: E501, EM102
            )

    @typing_extensions.override
    def __repr__(self) -> str:
        return f"OneOf({', '.join([repr(schema) for schema in self._schemas])})"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        frame: str = "\n".join(
            yaml_indent * indent + f"# {line}"
            for line in create_frame(
                "Chosse ONE of: "
                + ", ".join([f"`{schema.name}`" for schema in self._schemas]),
            ).split("\n")
        )

        return (
            frame
            + "\n"
            + "\n".join(
                [schema.to_formatted_string(indent=indent) for schema in self._schemas],
            )
        )


@typing.final
class AnyOf(Group):
    @typing_extensions.override
    def __call__(self, *schemas: str) -> None:
        if not any(schema.name in schemas for schema in self._schemas):
            raise ValueError(  # noqa: TRY003
                f"Expected at least one of {self._schemas}, but found no matches",  # noqa: EM102
            )

    @typing_extensions.override
    def __repr__(self) -> str:
        return f"AnyOf({', '.join([repr(schema) for schema in self._schemas])})"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        frame: str = "\n".join(
            yaml_indent * indent + f"# {line}"
            for line in create_frame(
                "Chosse ANY of: "
                + ", ".join([f"`{schema.name}`" for schema in self._schemas]),
            ).split("\n")
        )

        return (
            frame
            + "\n"
            + "\n".join(
                [schema.to_formatted_string(indent=indent) for schema in self._schemas],
            )
        )
