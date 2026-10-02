# These tests use unittest without adding a pytest dependency.
# ruff: noqa: PT009, PT027
from __future__ import annotations

import unittest
from collections.abc import Callable, Mapping
from importlib import import_module
from inspect import isabstract, signature
from itertools import product
from typing import cast

from confflow import Config
from confflow.core.errors import SchemaError, ValidationError, constraint_name
from confflow.core.schemas import Boolean, Integer, String, StringArray, Table
from confflow.core.schemas.table.constraints import (
    AtLeastOneOf,
    AtMostOneOf,
    Comparision,
    Constraint,
    Equal,
    ExactlyOneOf,
    Forbids,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    NotEqual,
    RequiredTogether,
    Requires,
)

_Factory = Callable[..., Constraint]


class _CustomTableConstraint(Constraint):
    __slots__ = ("calls",)

    def __init__(self) -> None:
        self.calls = 0

    @property
    def fields(self) -> tuple[str, ...]:
        return ("a", "b")

    def __call__(self, value: Mapping[str, object], /) -> None:
        self.calls += 1
        if value.get("a") != value.get("b"):
            raise ValueError("a and b must match")


class RelationalConstraintTest(unittest.TestCase):
    def test_positional_table_items_and_ordering(self) -> None:
        a = Integer("a", "", optional=True)
        b = Integer("b", "", optional=True)
        requires = Requires("a", "b")
        compare = LessThanOrEqual("a", "b")
        table = Table("t", "", a, b, requires, compare, optional=True)
        self.assertEqual(table.schemas, (a, b))
        self.assertEqual(table.constraints, (requires, compare))
        self.assertTrue(table.optional)
        table.validate({"a": 1, "b": 2})
        for items in ((requires, a, b), (a, requires, b)):
            with (
                self.subTest(items=items),
                self.assertRaisesRegex(SchemaError, "schemas must precede"),
            ):
                Table("t", "", *items)
        self.assertEqual(Table("empty", "").schemas, ())
        self.assertEqual(Table("empty", "").constraints, ())
        with self.assertRaisesRegex(SchemaError, "unknown table fields"):
            Table("t", "", requires)
        with self.assertRaisesRegex(SchemaError, "duplicate table schema name"):
            Table("t", "", a, a)
        constructor = cast("Callable[..., Table]", Table)
        for invalid in (object(), "field", 1, [requires]):
            with (
                self.subTest(invalid=invalid),
                self.assertRaisesRegex(
                    SchemaError, "items must be schemas or table constraints"
                ),
            ):
                constructor("t", "", invalid)
        self.assertNotIn("constraints", signature(Table).parameters)
        with self.assertRaises(TypeError):
            constructor("t", "", a, b, constraints=[requires])

    def test_all_table_presence_combinations(self) -> None:
        cases: tuple[tuple[_Factory, Callable[[Mapping[str, int]], bool]], ...] = (
            (Requires, lambda v: "a" not in v or ("b" in v and "c" in v)),
            (Forbids, lambda v: "a" not in v or ("b" not in v and "c" not in v)),
            (RequiredTogether, lambda v: len(v) in (0, 3)),
            (AtLeastOneOf, lambda v: len(v) >= 1),
            (AtMostOneOf, lambda v: len(v) <= 1),
            (ExactlyOneOf, lambda v: len(v) == 1),
            (Equal, lambda v: len(set(v.values())) <= 1),
            (NotEqual, lambda v: len(set(v.values())) == len(v)),
        )
        for factory, passes in cases:
            for mask in product((False, True), repeat=3):
                for raw in ((0, 0, 1), (0, 1, 2)):
                    value = {
                        name: item
                        for name, item, present in zip(
                            ("a", "b", "c"), raw, mask, strict=True
                        )
                        if present
                    }
                    schemas = tuple(
                        Integer(name, "", optional=True) for name in ("a", "b", "c")
                    )
                    local = Table("table", "", *schemas, factory("a", "b", "c"))
                    with self.subTest(rule=factory.__name__, value=value):
                        if passes(value):
                            local.validate(value)
                        else:
                            with self.assertRaises(ValidationError) as caught:
                                local.validate(value)
                            self.assertEqual(
                                caught.exception.constraint,
                                constraint_name(factory("a", "b", "c")),
                            )

    def test_comparison_operators_and_missing_operands(self) -> None:
        for factory, valid, invalid in (
            (Equal, (1, 1), (1, 2)),
            (NotEqual, (1, 2), (1, 1)),
            (LessThan, (1, 2), (1, 1)),
            (LessThanOrEqual, (1, 1), (2, 1)),
            (GreaterThan, (2, 1), (1, 1)),
            (GreaterThanOrEqual, (1, 1), (1, 2)),
        ):
            a = Integer("a", "", optional=True)
            b = Integer("b", "", optional=True)
            table = Table("t", "", a, b, factory("a", "b"))
            with self.subTest(constraint=factory.__name__):
                for missing in ({}, {"a": 0}, {"b": 0}):
                    table.validate(missing)
                table.validate(dict(zip(("a", "b"), valid, strict=True)))
                with self.assertRaises(ValidationError):
                    table.validate(dict(zip(("a", "b"), invalid, strict=True)))

    def test_imports_are_identical_classes_including_individual_modules(self) -> None:
        table = import_module("confflow.core.schemas.table.constraints")
        for name, module in (
            ("Requires", "requires"),
            ("Forbids", "forbids"),
            ("RequiredTogether", "required_together"),
            ("AtLeastOneOf", "at_least_one_of"),
            ("AtMostOneOf", "at_most_one_of"),
            ("ExactlyOneOf", "exactly_one_of"),
            ("Equal", "equal"),
            ("NotEqual", "not_equal"),
            ("LessThan", "comparision.less_than"),
            ("LessThanOrEqual", "comparision.less_than_or_equal"),
            ("GreaterThan", "comparision.greater_than"),
            ("GreaterThanOrEqual", "comparision.greater_than_or_equal"),
        ):
            with self.subTest(name=name):
                individual = import_module(
                    f"confflow.core.schemas.table.constraints.{module}"
                )
                self.assertIs(getattr(table, name), getattr(individual, name))
                self.assertTrue(issubclass(getattr(table, name), Constraint))
                self.assertEqual(
                    getattr(table, name).__module__,
                    f"confflow.core.schemas.table.constraints.{module}",
                )
        self.assertIs(
            Constraint,
            import_module("confflow.core.schemas.table.constraints.base").Constraint,
        )
        self.assertFalse(hasattr(table, "Compare"))

    def test_existing_custom_table_extension_contract(self) -> None:
        custom = _CustomTableConstraint()
        schema = Table("t", "", Integer("a", ""), Integer("b", ""), custom)
        schema.validate({"a": 1, "b": 1})
        with self.assertRaises(ValidationError) as caught:
            Config("Application", "", schema).validate({"t": {"a": 1, "b": 2}})
        self.assertEqual(custom.calls, 2)
        self.assertEqual(caught.exception.path, ("t",))
        self.assertEqual(caught.exception.constraint, "custom_table_constraint")
        self.assertEqual(caught.exception.value, {"a": 1, "b": 2})

    def test_existing_properties_repr_and_direct_calls(self) -> None:
        requires = Requires("a", "b", "c")
        self.assertEqual(requires.field, "a")
        self.assertEqual(requires.required, ("b", "c"))
        self.assertEqual(requires.fields, ("a", "b", "c"))
        self.assertEqual(repr(requires), "Requires(field='a', required=('b', 'c'))")
        requires({"a": False, "b": 0, "c": ""})
        with self.assertRaises(ValueError):
            requires({"a": False})
        compare = LessThan("a", "b")
        self.assertEqual((compare.left, compare.right), ("a", "b"))
        self.assertEqual(compare.fields, ("a", "b"))
        compare({"a": 0, "b": 1})
        self.assertEqual(repr(compare), "LessThan(left='a', right='b')")
        self.assertEqual(
            str(compare),
            'When both "a" and "b" are provided, "a" must be < "b"',
        )
        forbidden = Forbids("a", "b")
        self.assertEqual(forbidden.field, "a")
        self.assertEqual(forbidden.forbidden, ("b",))

    def test_comparision_base_and_normal_subclassing(self) -> None:
        self.assertTrue(isabstract(Comparision))
        module = import_module("confflow.core.schemas.table.constraints.comparision")
        self.assertIs(module.Comparision, Comparision)
        for factory in (LessThan, LessThanOrEqual, GreaterThan, GreaterThanOrEqual):
            self.assertTrue(issubclass(factory, Comparision))
            self.assertIs(getattr(module, factory.__name__), factory)
            self.assertFalse(hasattr(factory, "OPERATOR"))
            self.assertFalse(hasattr(factory, "_compare"))

        class SameLength(Comparision):
            def __call__(self, value: Mapping[str, object], /) -> None:
                if self.left not in value or self.right not in value:
                    return
                left, right = value[self.left], value[self.right]
                if not isinstance(left, str) or not isinstance(right, str):
                    raise TypeError("operands must be strings")
                if len(left) != len(right):
                    raise ValueError("operands must have the same length")

        constraint = SameLength("a", "b")
        self.assertEqual(constraint.fields, ("a", "b"))
        self.assertEqual(str(constraint), "")
        table = Table("t", "", String("a", ""), String("b", ""), constraint)
        table.validate({"a": "ab", "b": "cd"})
        with self.assertRaises(ValidationError) as caught:
            table.validate({"a": "a", "b": "cd"})
        self.assertEqual(caught.exception.constraint, "same_length")

    def test_invalid_operands_and_arities(self) -> None:
        a = "a"
        for factory in (
            RequiredTogether,
            AtLeastOneOf,
            AtMostOneOf,
            ExactlyOneOf,
            Equal,
            NotEqual,
        ):
            with self.subTest(rule=factory.__name__), self.assertRaises(SchemaError):
                factory(a, a)
            with self.assertRaises(SchemaError):
                factory()
            if factory is not AtLeastOneOf:
                with self.assertRaises(SchemaError):
                    factory(a)
        for factory in (Requires, Forbids):
            with self.assertRaises(SchemaError):
                factory(a)
            with self.assertRaises(SchemaError):
                factory(a, a)
            b = "b"
            with self.assertRaises(SchemaError):
                factory(a, b, b)
        for factory in (LessThan, LessThanOrEqual, GreaterThan, GreaterThanOrEqual):
            with self.subTest(constraint=factory.__name__):
                with self.assertRaises(SchemaError):
                    factory(a, a)
                with self.assertRaises(SchemaError):
                    factory("a", cast("str", []))
                with self.assertRaises(SchemaError):
                    factory(cast("str", 1), "b")
                with self.assertRaises(SchemaError):
                    Table("t", "", Integer("a", ""), factory("a", "missing"))

    def test_named_comparisons_report_incomparable_values(self) -> None:
        for factory in (LessThan, LessThanOrEqual, GreaterThan, GreaterThanOrEqual):
            constraint = factory("a", "b")
            table = Table("t", "", Integer("a", ""), String("b", ""), constraint)
            with self.subTest(constraint=factory.__name__):
                with self.assertRaisesRegex(ValueError, "cannot be compared"):
                    constraint({"a": 1, "b": "text"})
                with self.assertRaises(ValidationError) as caught:
                    table.validate({"a": 1, "b": "text"})
                self.assertEqual(
                    caught.exception.constraint, constraint_name(constraint)
                )
                self.assertEqual(caught.exception.value, {"a": 1, "b": "text"})

    def test_local_unknown_names_and_schema_operands_rejected(self) -> None:
        a = Integer("a", "")
        with self.assertRaises(SchemaError):
            Table("t", "", a, Requires("a", "missing"))
        with self.assertRaises(SchemaError):
            AtLeastOneOf(cast("str", a))

    def test_table_constraints_cannot_reach_descendants(self) -> None:
        nested = Table("nested", "", Integer("leaf", ""))
        for name in ("leaf", "nested.leaf"):
            with self.subTest(name=name), self.assertRaises(SchemaError):
                Table("parent", "", nested, AtLeastOneOf(name))
        table = Table("parent", "", nested, AtLeastOneOf("nested"))
        table.validate({"nested": {"leaf": 1}})

    def test_falsey_child_values_are_present(self) -> None:
        for child, value in (
            (Boolean("a", "", optional=True), False),
            (Integer("a", "", optional=True), 0),
            (String("a", "", optional=True), ""),
            (StringArray("a", "", optional=True), []),
            (Table("a", "", optional=True), {}),
        ):
            b = String("b", "", optional=True)
            with self.subTest(child=type(child).__name__):
                table = Table("t", "", child, b, Requires("a", "b"))
                with self.assertRaises(ValidationError):
                    table.validate({"a": value})
                table.validate({"a": value, "b": ""})
                Table("t", "", child, b, ExactlyOneOf("a", "b")).validate({"a": value})
                table = Table("t", "", child, b, Forbids("a", "b"))
                with self.assertRaises(ValidationError):
                    table.validate({"a": value, "b": ""})
