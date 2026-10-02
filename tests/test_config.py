# These tests use unittest without adding a pytest dependency.
# ruff: noqa: PT009, PT027
from __future__ import annotations

import unittest
from importlib.util import find_spec
from inspect import signature
from typing import TYPE_CHECKING, Any, cast

import confflow
from confflow import Configuration
from confflow.core.definitions.constraints.string import Length
from confflow.core.errors import SchemaError, ValidationError
from confflow.core.schemas import Integer, String, Table
from confflow.core.schemas.table.constraints import LessThanOrEqual, Requires

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from confflow.core.schemas.base import Schema


class ConfigTest(unittest.TestCase):
    def test_multiple_top_level_schemas(self) -> None:
        application = Table("application", "", String("name", ""))
        monitoring = Table("monitoring", "", String("endpoint", ""))
        workers = Integer("workers", "")
        config = Configuration(
            "Application", "Application configuration", application, monitoring, workers
        )
        self.assertEqual(config.name, "Application")
        self.assertEqual(config.description, "Application configuration")
        self.assertEqual(config.schemas, (application, monitoring, workers))
        config.validate(
            {
                "application": {"name": "example"},
                "monitoring": {"endpoint": "https://monitoring.example.com"},
                "workers": 4,
            }
        )

    def test_duplicate_top_level_names_rejected(self) -> None:
        with self.assertRaisesRegex(SchemaError, "duplicate table schema name"):
            Configuration(
                "Application",
                "",
                Integer("workers", ""),
                String("workers", ""),
            )

    def test_required_top_level_entries(self) -> None:
        for schema in (Integer("required", ""), Table("required", "")):
            with (
                self.subTest(schema=type(schema).__name__),
                self.assertRaises(ValidationError) as caught,
            ):
                Configuration("Application", "", schema).validate({})
            self.assertEqual(caught.exception.path, ("required",))
            self.assertEqual(caught.exception.expected, "required field")

    def test_optional_top_level_entries_may_be_omitted(self) -> None:
        config = Configuration(
            "Application",
            "",
            Integer("workers", "", optional=True),
            Table("monitoring", "", optional=True),
        )
        config.validate({})
        config.validate({"workers": 0, "monitoring": {}})

    def test_child_validation_propagates_with_path(self) -> None:
        config = Configuration("Application", "", Integer("workers", "", minimum=1))
        with self.assertRaises(ValidationError) as caught:
            config.validate({"workers": 0})
        self.assertEqual(caught.exception.path, ("workers",))
        self.assertEqual(caught.exception.value, 0)
        self.assertEqual(caught.exception.constraint, "range")

    def test_nested_tables_validate_normally(self) -> None:
        config = Configuration(
            "Application",
            "",
            Table("server", "", Table("limits", "", Integer("workers", ""))),
        )
        config.validate({"server": {"limits": {"workers": 4}}})
        with self.assertRaises(ValidationError) as caught:
            config.validate({"server": {"limits": {}}})
        self.assertEqual(caught.exception.path, ("server", "limits", "workers"))

    def test_table_constraints_are_preserved(self) -> None:
        authentication = Table(
            "authentication",
            "",
            String("username", "", optional=True),
            String("password", "", optional=True),
            Requires("username", "password"),
        )
        limits = Table(
            "limits",
            "",
            Integer("minimum", ""),
            Integer("maximum", ""),
            LessThanOrEqual("minimum", "maximum"),
        )
        config = Configuration(
            "Application",
            "",
            authentication,
            Table("server", "", limits),
        )
        config.validate(
            {
                "authentication": {"username": "service", "password": "secret"},
                "server": {"limits": {"minimum": 1, "maximum": 4}},
            }
        )
        with self.assertRaises(ValidationError) as caught:
            config.validate(
                {
                    "authentication": {"username": "service"},
                    "server": {"limits": {"minimum": 1, "maximum": 4}},
                }
            )
        self.assertEqual(caught.exception.path, ("authentication",))
        self.assertEqual(caught.exception.constraint, "requires")
        with self.assertRaises(ValidationError) as caught:
            config.validate(
                {
                    "authentication": {},
                    "server": {"limits": {"minimum": 4, "maximum": 1}},
                }
            )
        self.assertEqual(caught.exception.path, ("server", "limits"))
        self.assertEqual(caught.exception.constraint, "less_than_or_equal")

    def test_field_constraints_are_preserved(self) -> None:
        config = Configuration(
            "Application",
            "",
            Table("application", "", String("name", "", Length(minimum=1))),
        )
        config.validate({"application": {"name": "example"}})
        with self.assertRaises(ValidationError) as caught:
            config.validate({"application": {"name": ""}})
        self.assertEqual(caught.exception.path, ("application", "name"))
        self.assertEqual(caught.exception.constraint, "length")
        self.assertEqual(caught.exception.value, "")

    def test_unknown_top_level_entries_rejected(self) -> None:
        with self.assertRaises(ValidationError) as caught:
            Configuration("Application", "").validate({"unknown": 1})
        self.assertEqual(caught.exception.path, ("unknown",))
        self.assertEqual(caught.exception.expected, "declared table field")

    def test_invalid_root_value_and_schema(self) -> None:
        with self.assertRaises(ValidationError) as caught:
            Configuration("Application", "").validate(cast("Mapping[str, object]", []))
        self.assertEqual(caught.exception.expected, "configuration mapping")
        with self.assertRaises(SchemaError):
            Configuration("Application", "", cast("Schema[Any]", object()))

    def test_empty_configuration(self) -> None:
        config = Configuration("Application", "")
        self.assertEqual(config.schemas, ())
        config.validate({})

    def test_no_global_constraint_api(self) -> None:
        self.assertNotIn("constraints", signature(Configuration).parameters)
        self.assertFalse(hasattr(Configuration("Application", ""), "constraints"))
        constructor = cast("Callable[..., Configuration]", Configuration)
        with self.assertRaises(TypeError):
            constructor("Application", "", constraints=[])
        self.assertIsNone(find_spec("confflow.constraints"))
        for name in ("Requires", "Forbids", "Compare", "RelationalConstraint"):
            with self.subTest(name=name):
                self.assertFalse(hasattr(confflow, name))
