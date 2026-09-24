from __future__ import annotations

from typing import Generic

from typing_extensions import override

from confflow.core.shared import ConfigurationError, S, is_toml_value

from .base import Field


class Literal(Field[S], Generic[S]):
    def __init__(
        self,
        name: str,
        description: str,
        /,
        *values: S,
        required: bool = False,
        default: S | None = None,
    ) -> None:
        if not values:
            msg = "Literal requires at least one allowed value"
            raise ValueError(msg)

        if not all(
            is_toml_value(value) and not isinstance(value, (list, dict))
            for value in values
        ):
            msg = "Literal values must be TOML scalar values"
            raise TypeError(msg)

        if any(type(value) is not type(values[0]) for value in values[1:]):
            msg = "Literal values must all have the same type"
            raise TypeError(msg)

        if len(set(values)) != len(values):
            msg = "Literal values must be unique"
            raise ValueError(msg)

        self._values: tuple[S, ...] = values

        super().__init__(name, description, required=required, default=default)

    @property
    def values(self) -> tuple[S, ...]:
        return self._values

    @override
    def _typecheck(self, value: object, /) -> bool:
        return any(
            type(value) is type(allowed) and value == allowed for allowed in self.values
        )

    @override
    def validate(self, value: object, path: str, /) -> S:
        try:
            return super().validate(value, path)
        except ConfigurationError as exc:
            allowed: str = ", ".join(
                "true"
                if allowed is True
                else "false"
                if allowed is False
                else repr(allowed)
                for allowed in self.values
            )
            raise ConfigurationError(path, f"must be one of: {allowed}") from exc
