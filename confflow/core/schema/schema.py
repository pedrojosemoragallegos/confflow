from datetime import datetime
from typing import Dict, List, Optional, Set, Union

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
                Field[Dict[str, str]],
                Field[Dict[str, int]],
                Field[Dict[str, float]],
                Field[Dict[str, bool]],
                Field[Dict[str, datetime]],
                Field[Dict[str, bytes]],
                Field[List[str]],
                Field[List[int]],
                Field[List[float]],
                Field[List[bool]],
                Field[List[datetime]],
                Field[List[bytes]],
                Field[Set[str]],
                Field[Set[int]],
                Field[Set[float]],
                Field[Set[bool]],
                Field[Set[datetime]],
                Field[Set[bytes]],
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

    def addDictString(
        self,
        name: str,
        description: str,
        default_value: Optional[Dict[str, str]] = None,
        *constraint: FieldConstraint[Dict[str, str]],
    ):
        self._fields[name] = Field[Dict[str, str]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addDictInteger(
        self,
        name: str,
        description: str,
        default_value: Optional[Dict[str, int]] = None,
        *constraint: FieldConstraint[Dict[str, int]],
    ):
        self._fields[name] = Field[Dict[str, int]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addDictFloat(
        self,
        name: str,
        description: str,
        default_value: Optional[Dict[str, float]] = None,
        *constraint: FieldConstraint[Dict[str, float]],
    ):
        self._fields[name] = Field[Dict[str, float]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addDictBoolean(
        self,
        name: str,
        description: str,
        default_value: Optional[Dict[str, bool]] = None,
        *constraint: FieldConstraint[Dict[str, bool]],
    ):
        self._fields[name] = Field[Dict[str, bool]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addDictDate(
        self,
        name: str,
        description: str,
        default_value: Optional[Dict[str, datetime]] = None,
        *constraint: FieldConstraint[Dict[str, datetime]],
    ):
        self._fields[name] = Field[Dict[str, datetime]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addDictBytes(
        self,
        name: str,
        description: str,
        default_value: Optional[Dict[str, bytes]] = None,
        *constraint: FieldConstraint[Dict[str, bytes]],
    ):
        self._fields[name] = Field[Dict[str, bytes]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addListString(
        self,
        name: str,
        description: str,
        default_value: Optional[List[str]] = None,
        *constraint: FieldConstraint[List[str]],
    ):
        self._fields[name] = Field[List[str]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addListInteger(
        self,
        name: str,
        description: str,
        default_value: Optional[List[int]] = None,
        *constraint: FieldConstraint[List[int]],
    ):
        self._fields[name] = Field[List[int]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addListFloat(
        self,
        name: str,
        description: str,
        default_value: Optional[List[float]] = None,
        *constraint: FieldConstraint[List[float]],
    ):
        self._fields[name] = Field[List[float]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addListBoolean(
        self,
        name: str,
        description: str,
        default_value: Optional[List[bool]] = None,
        *constraint: FieldConstraint[List[bool]],
    ):
        self._fields[name] = Field[List[bool]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addListDate(
        self,
        name: str,
        description: str,
        default_value: Optional[List[datetime]] = None,
        *constraint: FieldConstraint[List[datetime]],
    ):
        self._fields[name] = Field[List[datetime]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addListBytes(
        self,
        name: str,
        description: str,
        default_value: Optional[List[bytes]] = None,
        *constraint: FieldConstraint[List[bytes]],
    ):
        self._fields[name] = Field[List[bytes]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addSetString(
        self,
        name: str,
        description: str,
        default_value: Optional[Set[str]] = None,
        *constraint: FieldConstraint[Set[str]],
    ):
        self._fields[name] = Field[Set[str]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addSetInteger(
        self,
        name: str,
        description: str,
        default_value: Optional[Set[int]] = None,
        *constraint: FieldConstraint[Set[int]],
    ):
        self._fields[name] = Field[Set[int]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addSetFloat(
        self,
        name: str,
        description: str,
        default_value: Optional[Set[float]] = None,
        *constraint: FieldConstraint[Set[float]],
    ):
        self._fields[name] = Field[Set[float]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addSetBoolean(
        self,
        name: str,
        description: str,
        default_value: Optional[Set[bool]] = None,
        *constraint: FieldConstraint[Set[bool]],
    ):
        self._fields[name] = Field[Set[bool]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addSetDate(
        self,
        name: str,
        description: str,
        default_value: Optional[Set[datetime]] = None,
        *constraint: FieldConstraint[Set[datetime]],
    ):
        self._fields[name] = Field[Set[datetime]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

    def addSetBytes(
        self,
        name: str,
        description: str,
        default_value: Optional[Set[bytes]] = None,
        *constraint: FieldConstraint[Set[bytes]],
    ):
        self._fields[name] = Field[Set[bytes]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            *constraint,
        )

        return self

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
