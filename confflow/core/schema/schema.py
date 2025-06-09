from datetime import datetime
from typing import Optional, Union

from ...types import DictValue, ListValue, SetValue
from ..config import FieldConstraint
from .field import Field


class Schema:
    def __init__(self, name: str, description: str):
        self._name = name
        self._description = description
        self._fields: dict[
            str,
            Union[
                Field[str],
                Field[int],
                Field[float],
                Field[bool],
                Field[datetime],
                Field[bytes],
                Field[DictValue],
                Field[ListValue],
                Field[SetValue],
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
        return self._fields.values()

    def addString(
        self,
        name: str,
        description: str,
        default_value: Optional[str] = None,
        *constraint: FieldConstraint[str],
    ):
        self._fields[name] = Field[str](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addInteger(
        self,
        name: str,
        description: str,
        default_value: Optional[int] = None,
        *constraint: FieldConstraint[int],
    ):
        self._fields[name] = Field[int](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addFloat(
        self,
        name: str,
        description: str,
        default_value: Optional[float] = None,
        *constraint: FieldConstraint[float],
    ):
        self._fields[name] = Field[float](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addBoolean(
        self,
        name: str,
        description: str,
        default_value: Optional[bool] = None,
        *constraint: FieldConstraint[bool],
    ):
        self._fields[name] = Field[bool](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addDate(
        self,
        name: str,
        description: str,
        default_value: Optional[datetime] = None,
        *constraint: FieldConstraint[datetime],
    ):
        self._fields[name] = Field[datetime](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addBytes(
        self,
        name: str,
        description: str,
        default_value: Optional[bytes] = None,
        *constraint: FieldConstraint[bytes],
    ):
        self._fields[name] = Field[bytes](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addList(
        self,
        name: str,
        description: str,
        default_value: Optional[ListValue] = None,
        *constraint: FieldConstraint[ListValue],
    ):
        self._fields[name] = Field[ListValue](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )
        return self

    def addMapping(
        self,
        name: str,
        description: str,
        default_value: Optional[DictValue] = None,
        *constraint: FieldConstraint[DictValue],
    ):
        self._fields[name] = Field[DictValue](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )
        return self

    # TODO create 'addEnum' and 'addSet'
    # def addEnum(
    #     self,
    #     name: str,
    #     description: str,
    #     values: list[str],
    #     default_value: Optional[str] = None,
    # ):
    #     self._fields[name] = Field[str](
    #         name=name,
    #         description=description,
    #         default_value=default_value,
    #         required=True if default_value else False,
    #         enum=values,
    #     )
    #     return self

    def keys(self):  # TODO add return type
        return self._fields.keys()

    def values(self):  # TODO add return type
        return self._fields.values()

    def items(self):  # TODO add return type
        return self._fields.items()

    def __getitem__(self, key: str):  # TODO add return type
        return self._fields[key]

    def __contains__(self, key: str):  # TODO add return type
        return key in self._fields

    # Only for iPython # TODO maybe remove here add as mixin or so
    def _ipython_key_completions_(self) -> list[str]:
        return list(self._fields.keys())
