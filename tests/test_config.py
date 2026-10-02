# These tests use unittest without adding a pytest dependency.
# ruff: noqa: PT009, PT027
from __future__ import annotations

import unittest
from importlib.util import find_spec
from inspect import signature
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any, cast

import tomlkit

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
    def load_value(
        self, config: Configuration, value: Mapping[str, object]
    ) -> Mapping[str, object]:
        with TemporaryDirectory() as directory:
            source = Path(directory) / "config.toml"
            source.write_text(tomlkit.dumps(dict(value)), encoding="utf-8")
            return config.load(source)

    def test_multiple_top_level_schemas(self) -> None:
        application = Table("application", "", String("name", ""))
        monitoring = Table("monitoring", "", String("endpoint", ""))
        workers = Integer("workers", "")
        config = Configuration(
            "Application", "Application configuration", application, monitoring, workers
        )
        self.load_value(
            config,
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
                self.load_value(Configuration("Application", "", schema), {})
            self.assertEqual(caught.exception.path, ("required",))
            self.assertEqual(caught.exception.expected, "required field")

    def test_optional_top_level_entries_may_be_omitted(self) -> None:
        config = Configuration(
            "Application",
            "",
            Integer("workers", "", optional=True),
            Table("monitoring", "", optional=True),
        )
        self.load_value(config, {})
        self.load_value(config, {"workers": 0, "monitoring": {}})

    def test_child_validation_propagates_with_path(self) -> None:
        config = Configuration("Application", "", Integer("workers", "", minimum=1))
        with self.assertRaises(ValidationError) as caught:
            self.load_value(config, {"workers": 0})
        self.assertEqual(caught.exception.path, ("workers",))
        self.assertEqual(caught.exception.value, 0)
        self.assertEqual(caught.exception.constraint, "range")

    def test_nested_tables_validate_normally(self) -> None:
        config = Configuration(
            "Application",
            "",
            Table("server", "", Table("limits", "", Integer("workers", ""))),
        )
        self.load_value(config, {"server": {"limits": {"workers": 4}}})
        with self.assertRaises(ValidationError) as caught:
            self.load_value(config, {"server": {"limits": {}}})
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
        self.load_value(
            config,
            {
                "authentication": {"username": "service", "password": "secret"},
                "server": {"limits": {"minimum": 1, "maximum": 4}},
            }
        )
        with self.assertRaises(ValidationError) as caught:
            self.load_value(
                config,
                {
                    "authentication": {"username": "service"},
                    "server": {"limits": {"minimum": 1, "maximum": 4}},
                }
            )
        self.assertEqual(caught.exception.path, ("authentication",))
        self.assertEqual(caught.exception.constraint, "requires")
        with self.assertRaises(ValidationError) as caught:
            self.load_value(
                config,
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
        self.load_value(config, {"application": {"name": "example"}})
        with self.assertRaises(ValidationError) as caught:
            self.load_value(config, {"application": {"name": ""}})
        self.assertEqual(caught.exception.path, ("application", "name"))
        self.assertEqual(caught.exception.constraint, "length")
        self.assertEqual(caught.exception.value, "")

    def test_unknown_top_level_entries_rejected(self) -> None:
        with self.assertRaises(ValidationError) as caught:
            self.load_value(Configuration("Application", ""), {"unknown": 1})
        self.assertEqual(caught.exception.path, ("unknown",))
        self.assertEqual(caught.exception.expected, "declared table field")

    def test_invalid_schema(self) -> None:
        with self.assertRaises(SchemaError):
            Configuration("Application", "", cast("Schema[Any]", object()))

    def test_empty_configuration(self) -> None:
        config = Configuration("Application", "")
        self.load_value(config, {})

    def test_schema_metadata_is_not_exposed(self) -> None:
        config = Configuration("Application", "Description", Integer("port", "Port"))
        for attribute in ("name", "description", "schemas", "validate"):
            with self.subTest(attribute=attribute):
                self.assertFalse(hasattr(config, attribute))

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
