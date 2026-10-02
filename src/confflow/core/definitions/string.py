from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from typing_extensions import override

from confflow.core.definitions.constraints.string import Length, Pattern

from .base import Definition

if TYPE_CHECKING:
    from confflow.core.definitions.constraints import Constraint


class String(Definition[str]):
    VALUE_TYPE: ClassVar[type[str]] = str

    def __init__(
        self,
        *constraints: Constraint[str],
        minimum: int | None = None,
        maximum: int | None = None,
        length: int | None = None,
        pattern: str | None = None,
    ) -> None:
        constraints: list[Constraint[str]] = list(constraints)

        if minimum is not None or maximum is not None or length is not None:
            constraints.append(Length(minimum=minimum, maximum=maximum, length=length))

        if pattern is not None:
            constraints.append(Pattern(pattern))

        # Reverse the constraints to maintain the intended order
        super().__init__(*reversed(constraints))

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}(constraints={self.constraints!r})"
