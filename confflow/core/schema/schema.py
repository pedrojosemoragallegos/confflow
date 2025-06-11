from datetime import datetime
from typing import Optional, Union

from ...types import ListValue
from ..config import FieldConstraint  # for typing
from .field import Field


class Schema:
    def __init__(self, name: str, description: str):
        self._name = name
        self._description = description
        self._entries: dict[  # TODO dict or ordered dict?
            str,
            Union[
                Field[str],
                Field[int],
                Field[float],
                Field[bool],
                Field[datetime],
                Field[bytes],
                Field[ListValue],
                "Schema",
            ],
        ] = dict()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def fields(self):  # TODO correct return type
        return self._entries.values()

    def SubSchema(self, name: str, schema: "Schema"):
        self._entries[name] = schema

        return self

    def String(
        self,
        name: str,
        description: str,
        default_value: Optional[str] = None,
        *constraint: FieldConstraint[str],
    ):
        self._entries[name] = Field[str](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def Integer(
        self,
        name: str,
        description: str,
        default_value: Optional[int] = None,
        *constraint: FieldConstraint[int],
    ):
        self._entries[name] = Field[int](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def Float(
        self,
        name: str,
        description: str,
        default_value: Optional[float] = None,
        *constraint: FieldConstraint[float],
    ):
        self._entries[name] = Field[float](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def Boolean(
        self,
        name: str,
        description: str,
        default_value: Optional[bool] = None,
        *constraint: FieldConstraint[bool],
    ):
        self._entries[name] = Field[bool](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def Date(
        self,
        name: str,
        description: str,
        default_value: Optional[datetime] = None,
        *constraint: FieldConstraint[datetime],
    ):
        self._entries[name] = Field[datetime](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def Bytes(
        self,
        name: str,
        description: str,
        default_value: Optional[bytes] = None,
        *constraint: FieldConstraint[bytes],
    ):
        self._entries[name] = Field[bytes](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def List(
        self,
        name: str,
        description: str,
        default_value: Optional[ListValue] = None,
        *constraint: FieldConstraint[ListValue],
    ):
        self._entries[name] = Field[ListValue](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )
        return self

    def keys(self):  # TODO  return type
        return self._entries.keys()

    def values(self):  # TODO  return type
        return self._entries.values()

    def items(self):  # TODO  return type
        return self._entries.items()

    def __getitem__(self, key: str):  # TODO  return type
        return self._entries[key]

    def __contains__(self, key: str):  # TODO  return type
        return key in self._entries

    # Only for iPython # TODO maybe remove here  as mixin or so
    def _ipython_key_completions_(self) -> list[str]:
        return list(self._entries.keys())
