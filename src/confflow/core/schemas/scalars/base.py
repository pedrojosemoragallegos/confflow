from __future__ import annotations

from typing import TYPE_CHECKING, Final, Generic, TypeVar

from typing_extensions import override

from confflow.core.definitions.constraints.literal import Literal
from confflow.core.errors import REDACTED_VALUE, ValidationError
from confflow.core.schemas.base import Schema
from confflow.core.types import Value

if TYPE_CHECKING:
    from confflow.core.definitions import Definition

ValueT = TypeVar(name="ValueT", bound=Value)


class Scalar(Schema[ValueT], Generic[ValueT]):
    __slots__ = ("__default", "__definition", "__secret")

    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *,
        optional: bool,
        definition: Definition[ValueT],
        default: ValueT | None = None,
        secret: bool = False,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[Definition[ValueT]] = definition
        self.__default: Final[ValueT | None] = default
        self.__secret: Final[bool] = secret
        if default is not None:
            try:
                Scalar.validate(self, default)
            except ValidationError as error:
                error.prepend_path(name)
                raise

    @property
    def secret(self) -> bool:
        return self.__secret

    @property
    def definition(self) -> Definition[ValueT]:
        return self.__definition

    @property
    def default(self) -> ValueT | None:
        return self.__default

    @override
    def redact_error(self, error: ValidationError, value: object, /) -> None:
        if self.__secret:
            error.redact(value)
            if self.__default is not None:
                error.redact(self.__default)
            for constraint in self.__definition.constraints:
                if isinstance(constraint, Literal):
                    for literal in constraint.values:
                        error.redact(literal)

    @override
    def validate(self, value: ValueT, /) -> None:
        if not self.__secret:
            self.__definition.validate(value)
            return
        try:
            self.__definition.validate(value)
        except ValidationError as error:
            self.redact_error(error, value)
            raise error from None
        except (TypeError, ValueError, RuntimeError) as cause:
            error = ValidationError(
                str(cause), value=value, expected=type(self).__name__
            )
            self.redact_error(error, value)
            raise error from None

    @override
    def __repr__(self) -> str:
        definition = REDACTED_VALUE if self.__secret else repr(self.__definition)
        default = (
            REDACTED_VALUE
            if self.__secret and self.__default is not None
            else repr(self.__default)
        )
        secret = ", secret=True" if self.__secret else ""
        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"definition={definition}, "
            f"default={default}{secret})"
        )
