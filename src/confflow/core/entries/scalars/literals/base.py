from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from ....definitions.base import Value as ScalarValue
from ..base import Scalar

if TYPE_CHECKING:
    from ....definitions.literals.base import Literal as LiteralDefinition

Value = TypeVar(name="Value", bound=ScalarValue)


class Literal(Scalar[Value], Generic[Value]):
    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *,
        optional: bool,
        default: Value | None,
        definition: LiteralDefinition[Value],
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=definition,
            default=default,
        )
