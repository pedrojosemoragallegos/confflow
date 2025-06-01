from __future__ import annotations

from typing import Iterable, Optional, Union, final, overload

from confflow.core.field import BoolField, FloatField, IntField, StrField
from confflow.core.field.constraints import Constraint

FieldTypes = Union[IntField, FloatField, BoolField, StrField]


@final
class Config:
    def __init__(self, name: str, description: str = "") -> None:
        self._name: str = name
        self._description: str = description
        self._fields: list[FieldTypes] = []

    @overload
    def addField(
        self,
        name: str,
        *,
        description: str,
        value: bool,
        default_value: Optional[bool] = ...,
        required: bool = ...,
        constraints: Optional[Iterable[Constraint[bool]]] = ...,
    ) -> Config: ...

    @overload
    def addField(
        self,
        name: str,
        *,
        description: str,
        value: int,
        default_value: Optional[int] = ...,
        required: bool = ...,
        constraints: Optional[Iterable[Constraint[int]]] = ...,
    ) -> Config: ...

    @overload
    def addField(
        self,
        name: str,
        *,
        description: str,
        value: float,
        default_value: Optional[float] = ...,
        required: bool = ...,
        constraints: Optional[Iterable[Constraint[float]]] = ...,
    ) -> Config: ...

    @overload
    def addField(
        self,
        name: str,
        *,
        description: str,
        value: str,
        default_value: Optional[str] = ...,
        required: bool = ...,
        constraints: Optional[Iterable[Constraint[str]]] = ...,
    ) -> Config: ...

    def addField(
        self,
        name: str,
        *,
        description: str = "",
        value: Union[bool, int, float, str],
        default_value: Optional[Union[bool, int, float, str]] = None,
        required: bool = False,
        constraints: Optional[
            Iterable[Constraint[Union[bool, int, float, str]]]
        ] = None,
    ) -> Config:
        if isinstance(value, bool):
            self._fields.append(
                BoolField(
                    name=name,
                    description=description,
                    value=value,
                    default_value=default_value,
                    required=required,
                    constraints=constraints,
                )
            )
        elif isinstance(value, int):
            self._fields.append(
                IntField(
                    name=name,
                    description=description,
                    value=value,
                    default_value=default_value,
                    required=required,
                    constraints=constraints,
                )
            )
        elif isinstance(value, float):
            self._fields.append(
                FloatField(
                    name=name,
                    description=description,
                    value=value,
                    default_value=default_value,
                    required=required,
                    constraints=constraints,
                )
            )
        elif isinstance(value, str):
            self._fields.append(
                StrField(
                    name=name,
                    description=description,
                    value=value,
                    default_value=default_value,
                    required=required,
                    constraints=constraints,
                )
            )
        else:
            raise TypeError(f"Unsupported type for value: {type(value).__name__}")

        return self
