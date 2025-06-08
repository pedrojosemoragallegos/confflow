from datetime import datetime
from typing import Dict, List, Optional, Set, Union

from confflow.core.field.constraint import Constraint

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
        required: bool = False,
        *constraint: Constraint[str],
    ):
        self._fields[name] = Field[str](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addInt(
        self,
        name: str,
        description: str,
        default_value: Optional[int] = None,
        required: bool = False,
        *constraint: Constraint[int],
    ):
        self._fields[name] = Field[int](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addFloat(
        self,
        name: str,
        description: str,
        default_value: Optional[float] = None,
        required: bool = False,
        *constraint: Constraint[float],
    ):
        self._fields[name] = Field[float](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addBool(
        self,
        name: str,
        description: str,
        default_value: Optional[bool] = None,
        required: bool = False,
        *constraint: Constraint[bool],
    ):
        self._fields[name] = Field[bool](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addDate(
        self,
        name: str,
        description: str,
        default_value: Optional[datetime] = None,
        required: bool = False,
        *constraint: Constraint[datetime],
    ):
        self._fields[name] = Field[datetime](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addBytes(
        self,
        name: str,
        description: str,
        default_value: Optional[bytes] = None,
        required: bool = False,
        *constraint: Constraint[bytes],
    ):
        self._fields[name] = Field[bytes](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addDictString(
        self,
        name: str,
        description: str,
        default_value: Optional[Dict[str, str]] = None,
        required: bool = False,
        *constraint: Constraint[Dict[str, str]],
    ):
        self._fields[name] = Field[Dict[str, str]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addDictInt(
        self,
        name: str,
        description: str,
        default_value: Optional[Dict[str, int]] = None,
        required: bool = False,
        *constraint: Constraint[Dict[str, int]],
    ):
        self._fields[name] = Field[Dict[str, int]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addDictFloat(
        self,
        name: str,
        description: str,
        default_value: Optional[Dict[str, float]] = None,
        required: bool = False,
        *constraint: Constraint[Dict[str, float]],
    ):
        self._fields[name] = Field[Dict[str, float]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addDictBool(
        self,
        name: str,
        description: str,
        default_value: Optional[Dict[str, bool]] = None,
        required: bool = False,
        *constraint: Constraint[Dict[str, bool]],
    ):
        self._fields[name] = Field[Dict[str, bool]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addDictDate(
        self,
        name: str,
        description: str,
        default_value: Optional[Dict[str, datetime]] = None,
        required: bool = False,
        *constraint: Constraint[Dict[str, datetime]],
    ):
        self._fields[name] = Field[Dict[str, datetime]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addDictBytes(
        self,
        name: str,
        description: str,
        default_value: Optional[Dict[str, bytes]] = None,
        required: bool = False,
        *constraint: Constraint[Dict[str, bytes]],
    ):
        self._fields[name] = Field[Dict[str, bytes]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addListString(
        self,
        name: str,
        description: str,
        default_value: Optional[List[str]] = None,
        required: bool = False,
        *constraint: Constraint[List[str]],
    ):
        self._fields[name] = Field[List[str]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addListInt(
        self,
        name: str,
        description: str,
        default_value: Optional[List[int]] = None,
        required: bool = False,
        *constraint: Constraint[List[int]],
    ):
        self._fields[name] = Field[List[int]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addListFloat(
        self,
        name: str,
        description: str,
        default_value: Optional[List[float]] = None,
        required: bool = False,
        *constraint: Constraint[List[float]],
    ):
        self._fields[name] = Field[List[float]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addListBool(
        self,
        name: str,
        description: str,
        default_value: Optional[List[bool]] = None,
        required: bool = False,
        *constraint: Constraint[List[bool]],
    ):
        self._fields[name] = Field[List[bool]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addListDate(
        self,
        name: str,
        description: str,
        default_value: Optional[List[datetime]] = None,
        required: bool = False,
        *constraint: Constraint[List[datetime]],
    ):
        self._fields[name] = Field[List[datetime]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addListBytes(
        self,
        name: str,
        description: str,
        default_value: Optional[List[bytes]] = None,
        required: bool = False,
        *constraint: Constraint[List[bytes]],
    ):
        self._fields[name] = Field[List[bytes]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addSetString(
        self,
        name: str,
        description: str,
        default_value: Optional[Set[str]] = None,
        required: bool = False,
        *constraint: Constraint[Set[str]],
    ):
        self._fields[name] = Field[Set[str]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addSetInt(
        self,
        name: str,
        description: str,
        default_value: Optional[Set[int]] = None,
        required: bool = False,
        *constraint: Constraint[Set[int]],
    ):
        self._fields[name] = Field[Set[int]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addSetFloat(
        self,
        name: str,
        description: str,
        default_value: Optional[Set[float]] = None,
        required: bool = False,
        *constraint: Constraint[Set[float]],
    ):
        self._fields[name] = Field[Set[float]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addSetBool(
        self,
        name: str,
        description: str,
        default_value: Optional[Set[bool]] = None,
        required: bool = False,
        *constraint: Constraint[Set[bool]],
    ):
        self._fields[name] = Field[Set[bool]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addSetDate(
        self,
        name: str,
        description: str,
        default_value: Optional[Set[datetime]] = None,
        required: bool = False,
        *constraint: Constraint[Set[datetime]],
    ):
        self._fields[name] = Field[Set[datetime]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            *constraint,
        )

        return self

    def addSetBytes(
        self,
        name: str,
        description: str,
        default_value: Optional[Set[bytes]] = None,
        required: bool = False,
        *constraint: Constraint[Set[bytes]],
    ):
        self._fields[name] = Field[Set[bytes]](
            name=name,
            description=description,
            default_value=default_value,
            required=required,
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
