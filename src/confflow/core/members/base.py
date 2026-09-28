from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Final

from .._validation import validate_name
from ..exceptions import SchemaError


class Entry(ABC):
    __slots__ = ("_description", "_name", "_required")

    def __init__(self, name: str, description: str, *, required: bool) -> None:
        self._name: Final[str] = validate_name(name, "member name")
        if type(description) is not str:
            raise SchemaError("member description must be a string")
        if type(required) is not bool:
            raise SchemaError("member required flag must be a boolean")

        self._description: Final[str] = description
        self._required: Final[bool] = required

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def required(self) -> bool:
        return self._required

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError
