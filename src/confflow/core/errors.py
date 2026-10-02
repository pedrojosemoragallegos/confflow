from __future__ import annotations

from re import sub
from typing import Final, TypeAlias

_PathPart: TypeAlias = str | int
_MISSING: Final[object] = object()


class SchemaError(ValueError):
    __slots__ = ()


class ValidationError(ValueError):
    __slots__ = (
        "_constraint",
        "_detail",
        "_expected",
        "_has_value",
        "_path",
        "_value",
    )

    _constraint: str | None
    _detail: str
    _expected: str | None
    _has_value: bool
    _path: tuple[_PathPart, ...]
    _value: object | None

    def __init__(
        self,
        detail: str,
        /,
        *,
        path: tuple[_PathPart, ...] = (),
        value: object = _MISSING,
        constraint: str | None = None,
        expected: str | None = None,
    ) -> None:
        super().__init__(detail)
        self._path: tuple[_PathPart, ...] = path
        self._has_value: bool = value is not _MISSING
        self._value: object | None = value if self._has_value else None
        self._constraint: str | None = constraint
        self._expected: str | None = expected
        self._detail: str = detail

    @property
    def constraint(self) -> str | None:
        return self._constraint

    @property
    def detail(self) -> str:
        return self._detail

    @property
    def expected(self) -> str | None:
        return self._expected

    @property
    def has_value(self) -> bool:
        return self._has_value

    @property
    def path(self) -> tuple[_PathPart, ...]:
        return self._path

    @property
    def value(self) -> object | None:
        return self._value

    def prepend_path(self, part: _PathPart, /) -> None:
        self._path: tuple[_PathPart, ...] = (part, *self._path)

    def __str__(self) -> str:
        if self._expected is not None and self._has_value:
            message = f"value {self._value!r} violates {self._expected}"
            if self._constraint is None and self._detail:
                message = f"{message} ({self._detail})"
        elif self._expected is not None:
            message = f"expected {self._expected}"
            if self._detail:
                message = f"{message} ({self._detail})"
        else:
            message: str = self._detail

        if not self._path:
            return message

        path: str = ""
        for part in self._path:
            if isinstance(part, int):
                path += f"[{part}]"
            elif isinstance(part, str) and part.startswith("["):
                path += part
            else:
                path += f".{part}" if path else str(part)

        return f"{path}: {message}"


def constraint_name(constraint: object, /) -> str:
    name = type(constraint).__name__.strip("_")
    name = sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def constraint_rule(constraint: object, /) -> str:
    name = constraint_name(constraint)
    if hasattr(constraint, "minimum") or hasattr(constraint, "maximum"):
        bounds: tuple[str, ...] = tuple(
            f"{field}={value!r}"
            for field in ("minimum", "maximum")
            if (value := getattr(constraint, field, None)) is not None
        )
        if bounds:
            return f"{name}({', '.join(bounds)})"

    representation: str = repr(constraint)
    class_name: str = type(constraint).__name__
    prefix: str = f"{class_name}("

    if representation.startswith(prefix):
        return f"{name}{representation[len(class_name) :]}"

    return name
