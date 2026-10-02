# These tests use unittest without adding a pytest dependency.
# ruff: noqa: PT009, PT027
from __future__ import annotations

import unittest
from datetime import UTC, date, datetime, time
from inspect import isabstract
from typing import TypeVar, get_args

from typing_extensions import get_original_bases

from confflow.core.definitions.constraints import (
    Boolean,
    Constraint,
    Float,
    Integer,
    LocalDate,
    LocalDateTime,
    LocalTime,
    OffsetDateTime,
    String,
)
from confflow.core.definitions.constraints.float import NotNaN, Range as FloatRange
from confflow.core.definitions.constraints.integer import Range as IntegerRange
from confflow.core.definitions.constraints.literal import Literal
from confflow.core.definitions.constraints.local_date import Range as LocalDateRange
from confflow.core.definitions.constraints.local_date_time import (
    Range as LocalDateTimeRange,
)
from confflow.core.definitions.constraints.local_time import Range as LocalTimeRange
from confflow.core.definitions.constraints.offset_date_time import (
    Range as OffsetDateTimeRange,
)
from confflow.core.definitions.constraints.string import Length, Pattern
from confflow.core.errors import ValidationError, constraint_name
from confflow.core.schemas import String as StringSchema
from confflow.core.types import Value

ValueT = TypeVar(name="ValueT", bound=Value)


class NonEmpty(String):
    __slots__ = ()

    def __call__(self, value: str, /) -> None:
        if not value:
            raise ValueError("string must not be empty")


class Enabled(Boolean):
    __slots__ = ()

    def __call__(self, value: bool, /) -> None:  # noqa: FBT001
        if not value:
            raise ValueError("value must be enabled")


class ConstraintBasesTest(unittest.TestCase):
    def test_identifiers_come_from_class_names(self) -> None:
        class HTTPValue(NonEmpty):
            pass

        for constraint, expected in (
            (NonEmpty(), "non_empty"),
            (Enabled(), "enabled"),
            (HTTPValue(), "http_value"),
            (IntegerRange(), "range"),
        ):
            with self.subTest(expected=expected):
                self.assertFalse(hasattr(constraint, "NAME"))
                self.assertEqual(constraint_name(constraint), expected)
        schema = StringSchema("name", "", HTTPValue())
        with self.assertRaises(ValidationError) as caught:
            schema.validate("")
        self.assertEqual(caught.exception.constraint, "http_value")

    def test_bases_are_abstract_and_specialize_supported_types(self) -> None:
        for base, value_type, module in (
            (Boolean, bool, "boolean"),
            (String, str, "string"),
            (Integer, int, "integer"),
            (Float, float, "float"),
            (LocalDate, date, "local_date"),
            (LocalTime, time, "local_time"),
            (LocalDateTime, datetime, "local_date_time"),
            (OffsetDateTime, datetime, "offset_date_time"),
        ):
            with self.subTest(base=base.__name__):
                self.assertTrue(issubclass(base, Constraint))
                self.assertTrue(isabstract(base))
                self.assertEqual(get_args(get_original_bases(base)[0]), (value_type,))
                self.assertEqual(base.__slots__, ())
                self.assertEqual(
                    base.__module__, f"confflow.core.definitions.constraints.{module}"
                )

    def test_builtin_constraints_inherit_typed_bases_and_keep_validation(self) -> None:
        self._check_constraint(Length(minimum=1), String, "text", "")
        self._check_constraint(Pattern(r"[a-z]+"), String, "text", "123")
        self._check_constraint(IntegerRange(minimum=1), Integer, 1, 0)
        self._check_constraint(FloatRange(minimum=1.0), Float, 1.0, 0.0)
        self._check_constraint(NotNaN(), Float, 1.0, float("nan"))
        self._check_constraint(
            LocalDateRange(minimum=date(2026, 1, 1)),
            LocalDate,
            date(2026, 1, 1),
            date(2025, 1, 1),
        )
        self._check_constraint(
            LocalTimeRange(minimum=time(1)), LocalTime, time(1), time(0)
        )
        self._check_constraint(
            LocalDateTimeRange(minimum=datetime.fromisoformat("2026-01-01T00:00:00")),
            LocalDateTime,
            datetime.fromisoformat("2026-01-01T00:00:00"),
            datetime.fromisoformat("2025-01-01T00:00:00"),
        )
        self._check_constraint(
            OffsetDateTimeRange(minimum=datetime(2026, 1, 1, tzinfo=UTC)),
            OffsetDateTime,
            datetime(2026, 1, 1, tzinfo=UTC),
            datetime(2025, 1, 1, tzinfo=UTC),
        )

    def _check_constraint(
        self,
        constraint: Constraint[ValueT],
        base: type[Constraint[ValueT]],
        valid: ValueT,
        invalid: ValueT,
    ) -> None:
        with self.subTest(base=base.__name__, constraint=type(constraint).__name__):
            self.assertIsInstance(constraint, base)
            constraint(valid)
            with self.assertRaises(ValueError):
                constraint(invalid)

    def test_custom_constraints_work_with_schemas(self) -> None:
        schema = StringSchema("name", "", NonEmpty())
        schema.validate("text")
        with self.assertRaises(ValidationError) as caught:
            schema.validate("")
        self.assertEqual(caught.exception.constraint, "non_empty")
        self.assertEqual(caught.exception.value, "")

        self.assertFalse(hasattr(NonEmpty(), "__dict__"))
        self.assertFalse(hasattr(Enabled(), "__dict__"))

    def test_custom_boolean_constraint(self) -> None:
        constraint = Enabled()
        constraint(True)  # noqa: FBT003
        with self.assertRaises(ValueError):
            constraint(False)  # noqa: FBT003

    def test_generic_literal_constraint_remains_supported(self) -> None:
        constraint = Literal("development", "production")
        self.assertIsInstance(constraint, Constraint)
        constraint("production")
        with self.assertRaises(ValueError):
            constraint("unknown")

    def test_human_readable_strings_are_separate_from_repr(self) -> None:
        cases = (
            (Length(minimum=1, maximum=64), "Length must be between 1 and 64"),
            (Length(length=3), "Length must be exactly 3"),
            (Length(minimum=1), "Length must be at least 1"),
            (Length(maximum=64), "Length must be at most 64"),
            (Length(), ""),
            (Pattern("[a-z]+"), 'Value must match the pattern "[a-z]+"'),
            (
                IntegerRange(minimum=1, maximum=65535),
                "Value must be between 1 and 65535",
            ),
            (IntegerRange(), ""),
            (FloatRange(minimum=0.0), "Value must be at least 0.0"),
            (NotNaN(), ""),
            (
                LocalDateRange(minimum=date(2026, 1, 1)),
                "Value must be at least 2026-01-01",
            ),
            (LocalTimeRange(maximum=time(2, 30)), "Value must be at most 02:30:00"),
            (
                LocalDateTimeRange(
                    minimum=datetime.fromisoformat("2026-01-01T09:00:00")
                ),
                "Value must be at least 2026-01-01T09:00:00",
            ),
            (
                OffsetDateTimeRange(maximum=datetime(2026, 1, 1, tzinfo=UTC)),
                "Value must be at most 2026-01-01T00:00:00Z",
            ),
            (
                Literal("development", "production"),
                'Value must be one of "development" or "production"',
            ),
            (
                Literal("development", "staging", "production"),
                'Value must be one of "development", "staging", or "production"',
            ),
            (Literal("production"), 'Value must be "production"'),
            (Literal(True, False), "Value must be one of true or false"),  # noqa: FBT003
            (NonEmpty(), ""),
        )
        for constraint, expected in cases:
            with self.subTest(constraint=type(constraint).__name__):
                self.assertEqual(str(constraint), expected)
        constraint = IntegerRange(minimum=1, maximum=4)
        self.assertEqual(repr(constraint), "Range(minimum=1, maximum=4)")
        self.assertEqual(repr(Literal("a", "b")), "Literal(values=('a', 'b'))")
