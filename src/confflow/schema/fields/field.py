from __future__ import annotations

import re
import typing
from datetime import datetime

import typing_extensions

from confflow.mixins import FormattedStringMixin
from confflow.shared import yaml_indent

from .constraint import (
    EnumValues,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    ListMaxLength,
    ListMinLength,
    MaxLength,
    MinLength,
    Regex,
)

T = typing.TypeVar("T")

if typing.TYPE_CHECKING:
    from .constraint import Constraint


## Base Field
class Field(FormattedStringMixin, typing.Generic[T]):
    SAFE_YAML_KEY = re.compile(r"^(?!-)(?!\d)[A-Za-z_][A-Za-z0-9_-]*$")

    def __init__(
        self,
        name: str,
        /,
        *constraints: Constraint[T],
        description: str | None = None,
        default: T | None = None,
    ) -> None:
        if not Field.SAFE_YAML_KEY.fullmatch(name):
            raise ValueError(  # noqa: TRY003
                f"Invalid YAML key name: {name!r}. "  # noqa: EM102
                "Must start with a letter or '_', not with '-' or digit, "
                "and may only contain letters, digits, underscores, or hyphens.",
            )

        if not description:
            raise ValueError("`description` should not be empty")  # noqa: EM101, TRY003

        self._name: str = name
        self._description: str | None = description
        self._default: T | None = default
        self._constraints: set[Constraint[T]] = set(constraints)
        self._dtype: str = "field"

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def default(self) -> T | None:
        return self._default

    def validate(self, value: T, /) -> None:
        for constraint in self._constraints:
            constraint(value)

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        description: str = yaml_indent * indent + f"# {self._description}\n"
        dtype: str = yaml_indent * indent + f"# type: {self._dtype}\n"
        constraints: str = (
            yaml_indent * indent
            + "# constraints:\n"
            + "".join(
                [
                    yaml_indent * indent
                    + "#  - "
                    + cnst.to_formatted_string(indent=indent + 1)
                    + "\n"
                    for cnst in self._constraints
                ],
            )
            if self._constraints
            else ""
        )

        if self.default is not None:
            default_value: str  # For typing
            field: str  # For typing
            if isinstance(self.default, datetime):  # Needed for YAML formatting
                default_value = self.default.isoformat()
            else:
                default_value = f"{self.default}"

            field = yaml_indent * indent + f"{self.name}: {default_value}"
        else:
            field = yaml_indent * indent + f"{self.name}:"

        return description + dtype + constraints + field

    def __repr__(self) -> str:
        return (
            "Field("
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"default={self._default!r}, "
            f"constraints={', '.join(repr(constraint) for constraint in self._constraints)}"  # noqa: E501
            ")"
        )


## Scalar Fields
class StringField(Field[str]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        /,
        *constraints: Constraint[str],
        description: str | None = None,
        default: str | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        regex: str | None = None,
        enum: list[str] | None = None,
    ) -> None:
        all_constraints: list[Constraint[str]] = list(constraints)
        if min_length is not None:
            all_constraints.append(MinLength(min_length))
        if max_length is not None:
            all_constraints.append(MaxLength(max_length))
        if regex is not None:
            all_constraints.append(Regex(regex))
        if enum is not None:
            all_constraints.append(EnumValues(enum))

        super().__init__(
            name,
            *all_constraints,
            description=description,
            default=default,
        )

        self._dtype = "string"


class IntegerField(Field[int]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        /,
        *constraints: Constraint[int],
        description: str | None = None,
        default: int | None = None,
        gt: int | None = None,
        ge: int | None = None,
        lt: int | None = None,
        le: int | None = None,
    ) -> None:
        """Initialize an integer field with optional constraints.

        Args:
            name (str): The name of the field.
            *constraints (Constraint[int]): Variable number of constraint objects to apply to the field.
            description (str | None, optional): A description of the field. Defaults to None.
            default (int | None, optional): The default value for the field. Defaults to None.
            gt (int | None, optional): Greater than constraint - field value must be greater than this. Defaults to None.
            ge (int | None, optional): Greater than or equal constraint - field value must be >= this. Defaults to None.
            lt (int | None, optional): Less than constraint - field value must be less than this. Defaults to None.
            le (int | None, optional): Less than or equal constraint - field value must be <= this. Defaults to None.

        """  # noqa: E501
        all_constraints: list[Constraint[int]] = list(constraints)
        if gt is not None:
            all_constraints.append(GreaterThan(gt))
        if ge is not None:
            all_constraints.append(GreaterThanOrEqual(ge))
        if lt is not None:
            all_constraints.append(LessThan(lt))
        if le is not None:
            all_constraints.append(LessThanOrEqual(le))

        super().__init__(
            name,
            *all_constraints,
            description=description,
            default=default,
        )

        self._dtype = "integer"


class FloatField(Field[float]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        /,
        *constraints: Constraint[float],
        description: str | None = None,
        default: float | None = None,
        gt: float | None = None,
        ge: float | None = None,
        lt: float | None = None,
        le: float | None = None,
    ) -> None:
        """Initialize a float field with optional constraints.

        Args:
            name (str): The name of the field.
            *constraints (Constraint[float]): Variable number of constraint objects to apply to the field.
            description (str | None, optional): A description of the field. Defaults to None.
            default (float | None, optional): The default value for the field. Defaults to None.
            gt (float | None, optional): Greater than constraint - field value must be greater than this. Defaults to None.
            ge (float | None, optional): Greater than or equal constraint - field value must be >= this. Defaults to None.
            lt (float | None, optional): Less than constraint - field value must be less than this. Defaults to None.
            le (float | None, optional): Less than or equal constraint - field value must be <= this. Defaults to None.

        """  # noqa: E501
        all_constraints: list[Constraint[float]] = list(constraints)
        if gt is not None:
            all_constraints.append(GreaterThan(gt))
        if ge is not None:
            all_constraints.append(GreaterThanOrEqual(ge))
        if lt is not None:
            all_constraints.append(LessThan(lt))
        if le is not None:
            all_constraints.append(LessThanOrEqual(le))

        super().__init__(
            name,
            *all_constraints,
            description=description,
            default=default,
        )

        self._dtype = "float"


class DateField(Field[datetime]):
    def __init__(
        self,
        name: str,
        /,
        *constraints: Constraint[datetime],
        description: str | None = None,
        default: datetime | None = None,
    ) -> None:
        """Initialize a date field with optional constraints.

        Args:
            name (str): The name of the field.
            *constraints (Constraint[datetime]): Variable number of constraint objects to apply to the field.
            description (str | None, optional): A description of the field. Defaults to None.
            default (datetime | None, optional): The default value for the field. Defaults to None.

        """  # noqa: E501
        super().__init__(
            name,
            *constraints,
            description=description,
            default=default,
        )

        self._dtype = "date"


class BytesField(Field[bytes]):
    def __init__(
        self,
        name: str,
        /,
        *constraints: Constraint[bytes],
        description: str | None = None,
        default: bytes | None = None,
    ) -> None:
        """Initialize a bytes field with optional constraints.

        Args:
            name (str): The name of the field.
            *constraints (Constraint[bytes]): Variable number of constraint objects to apply to the field.
            description (str | None, optional): A description of the field. Defaults to None.
            default (bytes | None, optional): The default value for the field. Defaults to None.

        """  # noqa: E501
        super().__init__(
            name,
            *constraints,
            description=description,
            default=default,
        )

        self._dtype = "bytes"


class BooleanField(Field[bool]):
    def __init__(
        self,
        name: str,
        /,
        *constraints: Constraint[bool],
        description: str | None = None,
        default: bool | None = None,
    ) -> None:
        """Initialize a boolean field with optional constraints.

        Args:
            name (str): The name of the field.
            *constraints (Constraint[bool]): Variable number of constraint objects to apply to the field.
            description (str | None, optional): A description of the field. Defaults to None.
            default (bool | None, optional): The default value for the field. Defaults to None.

        """  # noqa: E501
        super().__init__(
            name,
            *constraints,
            description=description,
            default=default,
        )

        self._dtype = "bool"


## List Fields
# TODO: create a base class for the ListFields otherwise we are repeating things
class Stringlist(Field[list[str]]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        /,
        *constraints: Constraint[list[str]],
        description: str | None = None,
        default: list[str] | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        item_min_length: int | None = None,
        item_max_length: int | None = None,
        item_regex: str | None = None,
        item_enum: list[str] | None = None,
    ) -> None:
        """Initialize a string list field with optional constraints.

        Args:
            name (str): The name of the field.
            *constraints (Constraint[list[str]]): Variable number of constraint objects to apply to the field.
            description (str | None, optional): A description of the field. Defaults to None.
            default (list[str] | None, optional): The default value for the field. Defaults to None.
            min_length (int | None, optional): Minimum number of items allowed in the list. Defaults to None.
            max_length (int | None, optional): Maximum number of items allowed in the list. Defaults to None.
            item_min_length (int | None, optional): Minimum length for each string item in the list. Defaults to None.
            item_max_length (int | None, optional): Maximum length for each string item in the list. Defaults to None.
            item_regex (str | None, optional): Regular expression pattern that each string item must match. Defaults to None.
            item_enum (list[str] | None, optional): List of allowed values for each string item. Defaults to None.

        """  # noqa: E501
        all_constraints: list[Constraint[list[str]]] = list(constraints)
        if min_length is not None:
            all_constraints.append(ListMinLength[str](min_length))
        if max_length is not None:
            all_constraints.append(ListMaxLength[str](max_length))

        super().__init__(
            name,
            *all_constraints,
            description=description,
            default=default,
        )

        self._dtype = "list[string]"

        self._item_constraints: list[Constraint[str]] = []
        if item_min_length is not None:
            self._item_constraints.append(MinLength(item_min_length))
        if item_max_length is not None:
            self._item_constraints.append(MaxLength(item_max_length))
        if item_regex is not None:
            self._item_constraints.append(Regex(item_regex))
        if item_enum is not None:
            self._item_constraints.append(EnumValues(item_enum))

    @typing_extensions.override
    def validate(self, value: list[str], /) -> None:
        # Validate list-level constraints
        super().validate(value)
        # Validate each item
        for item in value:
            for constraint in self._item_constraints:
                constraint(item)

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        description: str = yaml_indent * indent + f"# {self._description}\n"
        dtype: str = yaml_indent * indent + "# type: list[str]\n"
        constraints: str = (
            yaml_indent * indent
            + "# constraints:\n"
            + "".join(
                [
                    yaml_indent * indent
                    + "#  - "
                    + cnst.to_formatted_string(indent=indent + 1)
                    + "\n"
                    for cnst in self._constraints
                ],
            )
            if self._constraints
            else ""
        )

        field: str  # For typing
        if self.default:
            field = yaml_indent * indent + f"{self.name}: {self.default}"
        else:
            field = yaml_indent * indent + f"{self.name}: []"

        return description + dtype + constraints + field


class Integerlist(Field[list[int]]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        /,
        *constraints: Constraint[list[int]],
        description: str | None = None,
        default: list[int] | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        item_gt: int | None = None,
        item_ge: int | None = None,
        item_lt: int | None = None,
        item_le: int | None = None,
    ) -> None:
        """Initialize an integer list field with optional constraints.

        Args:
            name (str): The name of the field.
            *constraints (Constraint[list[int]]): Variable number of constraint objects to apply to the field.
            description (str | None, optional): A description of the field. Defaults to None.
            default (list[int] | None, optional): The default value for the field. Defaults to None.
            min_length (int | None, optional): Minimum number of items allowed in the list. Defaults to None.
            max_length (int | None, optional): Maximum number of items allowed in the list. Defaults to None.
            item_gt (int | None, optional): Each integer item must be greater than this value. Defaults to None.
            item_ge (int | None, optional): Each integer item must be greater than or equal to this value. Defaults to None.
            item_lt (int | None, optional): Each integer item must be less than this value. Defaults to None.
            item_le (int | None, optional): Each integer item must be less than or equal to this value. Defaults to None.

        """  # noqa: E501
        all_constraints: list[Constraint[list[int]]] = list(constraints)
        if min_length is not None:
            all_constraints.append(ListMinLength[int](min_length))
        if max_length is not None:
            all_constraints.append(ListMaxLength[int](max_length))

        super().__init__(
            name,
            *all_constraints,
            description=description,
            default=default,
        )

        self._dtype = "list[integer]"

        self._item_constraints: list[Constraint[int]] = []
        if item_gt is not None:
            self._item_constraints.append(GreaterThan(item_gt))
        if item_ge is not None:
            self._item_constraints.append(GreaterThanOrEqual(item_ge))
        if item_lt is not None:
            self._item_constraints.append(LessThan(item_lt))
        if item_le is not None:
            self._item_constraints.append(LessThanOrEqual(item_le))

    @typing_extensions.override
    def validate(self, value: list[int], /) -> None:
        # Validate list-level constraints
        super().validate(value)
        # Validate each item
        for item in value:
            for constraint in self._item_constraints:
                constraint(item)

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        description: str = yaml_indent * indent + f"# {self._description}\n"
        dtype: str = yaml_indent * indent + "# type: list[int]\n"
        constraints: str = (
            yaml_indent * indent
            + "# constraints:\n"
            + "".join(
                [
                    yaml_indent * indent
                    + "#  - "
                    + cnst.to_formatted_string(indent=indent + 1)
                    + "\n"
                    for cnst in self._constraints
                ],
            )
            if self._constraints
            else ""
        )

        field: str  # For typing
        if self.default:
            field = yaml_indent * indent + f"{self.name}: {self.default}"
        else:
            field = yaml_indent * indent + f"{self.name}: []"

        return description + dtype + constraints + field


class Floatlist(Field[list[float]]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        /,
        *constraints: Constraint[list[float]],
        description: str | None = None,
        default: list[float] | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        item_gt: float | None = None,
        item_ge: float | None = None,
        item_lt: float | None = None,
        item_le: float | None = None,
    ) -> None:
        """Initialize a float list field with optional constraints.

        Args:
            name (str): The name of the field.
            *constraints (Constraint[list[float]]): Variable number of constraint objects to apply to the field.
            description (str | None, optional): A description of the field. Defaults to None.
            default (list[float] | None, optional): The default value for the field. Defaults to None.
            min_length (int | None, optional): Minimum number of items allowed in the list. Defaults to None.
            max_length (int | None, optional): Maximum number of items allowed in the list. Defaults to None.
            item_gt (float | None, optional): Each float item must be greater than this value. Defaults to None.
            item_ge (float | None, optional): Each float item must be greater than or equal to this value. Defaults to None.
            item_lt (float | None, optional): Each float item must be less than this value. Defaults to None.
            item_le (float | None, optional): Each float item must be less than or equal to this value. Defaults to None.

        """  # noqa: E501
        all_constraints: list[Constraint[list[float]]] = list(constraints)
        if min_length is not None:
            all_constraints.append(ListMinLength[float](min_length))
        if max_length is not None:
            all_constraints.append(ListMaxLength[float](max_length))

        super().__init__(
            name,
            *all_constraints,
            description=description,
            default=default,
        )

        self._dtype = "list[floating]"

        self._item_constraints: list[Constraint[float]] = []
        if item_gt is not None:
            self._item_constraints.append(GreaterThan(item_gt))
        if item_ge is not None:
            self._item_constraints.append(GreaterThanOrEqual(item_ge))
        if item_lt is not None:
            self._item_constraints.append(LessThan(item_lt))
        if item_le is not None:
            self._item_constraints.append(LessThanOrEqual(item_le))

    @typing_extensions.override
    def validate(self, value: list[float], /) -> None:
        # Validate list-level constraints
        super().validate(value)
        # Validate each item
        for item in value:
            for constraint in self._item_constraints:
                constraint(item)

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        description: str = yaml_indent * indent + f"# {self._description}\n"
        dtype: str = yaml_indent * indent + "# type: list[float]\n"
        constraints: str = (
            yaml_indent * indent
            + "# constraints:\n"
            + "".join(
                [
                    yaml_indent * indent
                    + "#  - "
                    + cnst.to_formatted_string(indent=indent + 1)
                    + "\n"
                    for cnst in self._constraints
                ],
            )
            if self._constraints
            else ""
        )

        field: str  # For typing
        if self.default:
            field = yaml_indent * indent + f"{self.name}: {self.default}"
        else:
            field = yaml_indent * indent + f"{self.name}: []"

        return description + dtype + constraints + field


class Booleanlist(Field[list[bool]]):
    def __init__(
        self,
        name: str,
        /,
        *constraints: Constraint[list[bool]],
        description: str | None = None,
        default: list[bool] | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> None:
        """Initialize a boolean list field with optional constraints.

        Args:
            name (str): The name of the field.
            *constraints (Constraint[list[bool]]): Variable number of constraint objects to apply to the field.
            description (str | None, optional): A description of the field. Defaults to None.
            default (list[bool] | None, optional): The default value for the field. Defaults to None.
            min_length (int | None, optional): Minimum number of items allowed in the list. Defaults to None.
            max_length (int | None, optional): Maximum number of items allowed in the list. Defaults to None.

        """  # noqa: E501
        all_constraints: list[Constraint[list[bool]]] = list(constraints)
        if min_length is not None:
            all_constraints.append(ListMinLength[bool](min_length))
        if max_length is not None:
            all_constraints.append(ListMaxLength[bool](max_length))

        super().__init__(
            name,
            *all_constraints,
            description=description,
            default=default,
        )

        self._dtype = "list[boolean]"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        description: str = yaml_indent * indent + f"# {self._description}\n"
        dtype: str = yaml_indent * indent + "# type: list[bool]\n"
        constraints: str = (
            yaml_indent * indent
            + "# constraints:\n"
            + "".join(
                [
                    yaml_indent * indent
                    + "#  - "
                    + cnst.to_formatted_string(indent=indent + 1)
                    + "\n"
                    for cnst in self._constraints
                ],
            )
            if self._constraints
            else ""
        )

        field: str  # For typing
        if self.default:
            field = yaml_indent * indent + f"{self.name}: {self.default}"
        else:
            field = yaml_indent * indent + f"{self.name}: []"

        return description + dtype + constraints + field


class Datelist(Field[list[datetime]]):
    def __init__(
        self,
        name: str,
        /,
        *constraints: Constraint[list[datetime]],
        description: str | None = None,
        default: list[datetime] | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> None:
        """Initialize a datetime list field with optional constraints.

        Args:
            name (str): The name of the field.
            *constraints (Constraint[list[datetime]]): Variable number of constraint objects to apply to the field.
            description (str | None, optional): A description of the field. Defaults to None.
            default (list[datetime] | None, optional): The default value for the field. Defaults to None.
            min_length (int | None, optional): Minimum number of items allowed in the list. Defaults to None.
            max_length (int | None, optional): Maximum number of items allowed in the list. Defaults to None.

        """  # noqa: E501
        all_constraints: list[Constraint[list[datetime]]] = list(constraints)
        if min_length is not None:
            all_constraints.append(ListMinLength[datetime](min_length))
        if max_length is not None:
            all_constraints.append(ListMaxLength[datetime](max_length))

        super().__init__(
            name,
            *all_constraints,
            description=description,
            default=default,
        )

        self._dtype = "list[date]"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        description: str = yaml_indent * indent + f"# {self._description}\n"
        dtype: str = yaml_indent * indent + "# type: list[datetime]\n"
        constraints: str = (
            yaml_indent * indent
            + "# constraints:\n"
            + "".join(
                [
                    yaml_indent * indent
                    + "#  - "
                    + cnst.to_formatted_string(indent=indent + 1)
                    + "\n"
                    for cnst in self._constraints
                ],
            )
            if self._constraints
            else ""
        )

        field: str  # For typing
        if self.default:
            field = (
                yaml_indent * indent
                + f"{self.name}: [{', '.join([item.isoformat() for item in self.default])}]"  # noqa: E501# noqa: Q000
            )
        else:
            field = yaml_indent * indent + f"{self.name}: []"

        return description + dtype + constraints + field


class Byteslist(Field[list[bytes]]):
    def __init__(
        self,
        name: str,
        /,
        *constraints: Constraint[list[bytes]],
        description: str | None = None,
        default: list[bytes] | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> None:
        """Initialize a bytes list field with optional constraints.

        Args:
            name (str): The name of the field.
            *constraints (Constraint[list[bytes]]): Variable number of constraint objects to apply to the field.
            description (str | None, optional): A description of the field. Defaults to None.
            default (list[bytes] | None, optional): The default value for the field. Defaults to None.
            min_length (int | None, optional): Minimum number of items allowed in the list. Defaults to None.
            max_length (int | None, optional): Maximum number of items allowed in the list. Defaults to None.

        """  # noqa: E501
        all_constraints: list[Constraint[list[bytes]]] = list(constraints)
        if min_length is not None:
            all_constraints.append(ListMinLength[bytes](min_length))
        if max_length is not None:
            all_constraints.append(ListMaxLength[bytes](max_length))

        super().__init__(
            name,
            *all_constraints,
            description=description,
            default=default,
        )

        self._dtype = "list[bytes]"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        description: str = yaml_indent * indent + f"# {self._description}\n"
        dtype: str = yaml_indent * indent + "# type: list[bytes]\n"
        constraints: str = (
            yaml_indent * indent
            + "# constraints:\n"
            + "".join(
                [
                    yaml_indent * indent
                    + "#  - "
                    + cnst.to_formatted_string(indent=indent + 1)
                    + "\n"
                    for cnst in self._constraints
                ],
            )
            if self._constraints
            else ""
        )

        field: str  # For typing
        if self.default:
            field = yaml_indent * indent + f"{self.name}: {self.default}"
        else:
            field = yaml_indent * indent + f"{self.name}: []"

        return description + dtype + constraints + field
