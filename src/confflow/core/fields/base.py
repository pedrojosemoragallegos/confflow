from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, cast

from confflow.core.shared import ConfigurationError, T_co, TOMLValue, validate_name


class Field(ABC, Generic[T_co]):
    def __init__(
        self,
        name: str,
        description: str,
        /,
        *,
        required: bool = False,
        default: TOMLValue | None = None,
    ) -> None:
        validate_name(name)

        if required and default is not None:
            msg = f"{name}: a required field cannot have a default"
            raise ValueError(msg)

        self._name: str = name
        self._description: str = description
        self._required: bool = required
        self._default: T_co | None = None

        if default is not None:
            self._default: T_co = self.validate(default, name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def required(self) -> bool:
        return self._required

    @property
    def default(self) -> T_co | None:
        return self._default

    @abstractmethod
    def _typecheck(self, value: object, /) -> bool: ...

    def validate(self, value: object, path: str, /) -> T_co:
        if not self._typecheck(value):
            msg = f"invalid {type(self).__name__} value"
            raise ConfigurationError(path, msg)

        return cast(typ="T_co", val=value)
