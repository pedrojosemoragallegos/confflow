# These tests use unittest without adding a pytest dependency.
# ruff: noqa: PT009, PT027
from __future__ import annotations

import os
import unittest
from datetime import UTC, date, datetime, time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import patch

import tomlkit

from confflow import Configuration
from confflow.core.errors import ValidationError
from confflow.core.schemas import (
    Boolean,
    BooleanArray,
    Float,
    FloatArray,
    Integer,
    IntegerArray,
    LocalDate,
    LocalDateArray,
    LocalDateTime,
    LocalDateTimeArray,
    LocalTime,
    LocalTimeArray,
    Mapping,
    NestedArray,
    OffsetDateTime,
    OffsetDateTimeArray,
    String,
    StringArray,
    Table,
    TableArray,
)
from confflow.core.schemas.table.constraints import LessThanOrEqual

if TYPE_CHECKING:
    from collections.abc import Mapping as MappingABC

    from confflow.core.schemas.base import Schema


class EnvironmentTest(unittest.TestCase):
    def load_value(
        self,
        config: Configuration,
        value: MappingABC[str, object],
        environment: MappingABC[str, str],
    ) -> MappingABC[str, object]:
        with (
            TemporaryDirectory() as directory,
            patch.dict(os.environ, environment, clear=True),
        ):
            source = Path(directory) / "config.toml"
            content = tomlkit.dumps(dict(value))
            source.write_text(content, encoding="utf-8")
            loaded = config.load(source)
            self.assertEqual(source.read_text(encoding="utf-8"), content)
            return loaded

    def test_scalar_conversions_and_array_items(self) -> None:
        cases = (
            (String, StringArray, "secret-value", "secret-value"),
            (Integer, IntegerArray, "8080", 8080),
            (Float, FloatArray, "0.5", 0.5),
            (Float, FloatArray, "2", 2.0),
            (Boolean, BooleanArray, "true", True),
            (Boolean, BooleanArray, "false", False),
            (LocalDate, LocalDateArray, "2026-10-03", date(2026, 10, 3)),
            (LocalTime, LocalTimeArray, "12:34:56.123", time(12, 34, 56, 123000)),
            (
                LocalDateTime,
                LocalDateTimeArray,
                "2026-10-03T12:34:56",
                datetime(2026, 10, 3, 12, 34, 56),  # noqa: DTZ001
            ),
            (
                OffsetDateTime,
                OffsetDateTimeArray,
                "2026-10-03T12:34:56Z",
                datetime(2026, 10, 3, 12, 34, 56, tzinfo=UTC),
            ),
        )
        for scalar, array, raw, expected in cases:
            with self.subTest(scalar=scalar, raw=raw):
                config = Configuration(
                    "Application", "", scalar("value", ""), array("items", "")
                )
                loaded = self.load_value(
                    config,
                    {"value": "$VALUE", "items": ["$VALUE"]},
                    {"VALUE": raw},
                )
                self.assertEqual(loaded, {"value": expected, "items": (expected,)})
                self.assertIs(type(loaded["value"]), type(expected))
                self.assertIs(
                    type(cast("tuple[object, ...]", loaded["items"])[0]), type(expected)
                )

    def test_nested_container_traversal(self) -> None:
        config = Configuration(
            "Application",
            "",
            Table("server", "", Integer("port", "")),
            NestedArray("ports", "", array=IntegerArray("row", "")),
            Mapping("limits", "", value=Integer("limit", "")),
            Mapping("servers", "", value=Table("server", "", Integer("port", ""))),
            Mapping("groups", "", value=IntegerArray("ports", "")),
            TableArray("backends", "", Table("backend", "", Integer("port", ""))),
        )
        loaded = self.load_value(
            config,
            {
                "server": {"port": "$PORT"},
                "ports": [["$PORT", 80], ["$PORT"]],
                "limits": {"main": "$PORT"},
                "servers": {"main": {"port": "$PORT"}},
                "groups": {"main": ["$PORT"]},
                "backends": [{"port": "$PORT"}],
            },
            {"PORT": "8080"},
        )
        self.assertEqual(
            loaded,
            {
                "server": {"port": 8080},
                "ports": ((8080, 80), (8080,)),
                "limits": {"main": 8080},
                "servers": {"main": {"port": 8080}},
                "groups": {"main": (8080,)},
                "backends": ({"port": 8080},),
            },
        )
        with self.assertRaises(TypeError):
            cast("dict[str, object]", loaded)["new"] = "value"
        with self.assertRaises(TypeError):
            cast("dict[str, object]", loaded["server"])["port"] = 1
        backend = cast("tuple[dict[str, object], ...]", loaded["backends"])[0]
        with self.assertRaises(TypeError):
            backend["port"] = 1

    def test_exact_matching_and_single_pass_escaping(self) -> None:
        config = Configuration("Application", "", StringArray("values", ""))
        literals = (
            "$$HOST",
            "hello $HOST",
            "$5",
            "$HOST/path",
            "$$5",
            "$$HOST/path",
            "$HOST\n",
            "$",
            "$$$HOST",
            "${HOST}",
            "$HÖST",
            "",
        )
        loaded = self.load_value(config, {"values": list(literals)}, {"HOST": "host"})
        self.assertEqual(loaded["values"], ("$HOST", *literals[1:]))
        self.assertEqual(
            self.load_value(
                config, {"values": ["$$HOST", "$_HOST_2"]}, {"_HOST_2": "host"}
            )["values"],
            ("$HOST", "host"),
        )
        for raw in ("$MISSING", "$$HOST", ""):
            with self.subTest(raw=raw):
                self.assertEqual(
                    self.load_value(config, {"values": ["$HOST"]}, {"HOST": raw})[
                        "values"
                    ],
                    (raw,),
                )

    def test_string_reference_and_literal_strings(self) -> None:
        config = Configuration("Application", "", String("host", ""))
        cases = (
            ("$HOST", "localhost"),
            ("$$HOST", "$HOST"),
            ("hello $HOST", "hello $HOST"),
            ("$5", "$5"),
            ("$HOST/path", "$HOST/path"),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(
                    self.load_value(config, {"host": value}, {"HOST": "localhost"}),
                    {"host": expected},
                )
        self.assertEqual(
            self.load_value(config, {"host": "$$HOST"}, {}), {"host": "$HOST"}
        )
        with self.assertRaises(ValidationError) as caught:
            self.load_value(config, {"host": "$HOST"}, {})
        self.assertEqual(caught.exception.path, ("host",))
        self.assertIn("HOST", caught.exception.detail)

    def test_missing_and_invalid_values_preserve_paths(self) -> None:
        cases = (
            (Integer("port", ""), {"port": "$PORT"}, ("port",)),
            (
                Table("server", "", Integer("port", "")),
                {"server": {"port": "$PORT"}},
                ("server", "port"),
            ),
            (IntegerArray("ports", ""), {"ports": ["$PORT"]}, ("ports", 0)),
            (
                NestedArray("ports", "", array=IntegerArray("row", "")),
                {"ports": [["$PORT"]]},
                ("ports", 0, 0),
            ),
            (
                Mapping("ports", "", value=Integer("port", "")),
                {"ports": {"main": "$PORT"}},
                ("ports", "['main']"),
            ),
            (
                TableArray("servers", "", Table("server", "", Integer("port", ""))),
                {"servers": [{"port": "$PORT"}]},
                ("servers", 0, "port"),
            ),
        )
        for schema, value, path in cases:
            for environment in ({}, {"PORT": "abc"}):
                with (
                    self.subTest(schema=schema, environment=environment),
                    self.assertRaises(ValidationError) as caught,
                ):
                    self.load_value(
                        Configuration("Application", "", schema), value, environment
                    )
                self.assertEqual(caught.exception.path, path)
                self.assertEqual(caught.exception.value, "$PORT")
                self.assertIn("PORT", str(caught.exception))
                self.assertIn(
                    "not set" if not environment else "cannot be converted",
                    caught.exception.detail,
                )

    def test_invalid_scalar_conversions(self) -> None:
        cases = (
            (Integer, "1.5"),
            (Float, "abc"),
            (Boolean, "TRUE"),
            (Boolean, "1"),
            (Boolean, ""),
            (LocalDate, "2026-02-30"),
            (LocalTime, "25:00:00"),
            (LocalDateTime, "not-a-datetime"),
            (OffsetDateTime, "not-a-datetime"),
        )
        for scalar, raw in cases:
            with (
                self.subTest(scalar=scalar, raw=raw),
                self.assertRaises(ValidationError) as caught,
            ):
                self.load_value(
                    Configuration("Application", "", scalar("value", "")),
                    {"value": "$VALUE"},
                    {"VALUE": raw},
                )
            self.assertEqual(caught.exception.path, ("value",))
            self.assertIn("cannot be converted", caught.exception.detail)

    def test_schema_validation_after_conversion(self) -> None:
        cases = (
            (Integer("value", "", minimum=1), "0"),
            (Float("value", ""), "nan"),
            (String("value", "", minimum=1), ""),
            (OffsetDateTime("value", ""), "2026-10-03T12:34:56"),
        )
        for schema, raw in cases:
            with (
                self.subTest(schema=schema),
                self.assertRaises(ValidationError) as caught,
            ):
                self.load_value(
                    Configuration("Application", "", schema),
                    {"value": "$VALUE"},
                    {"VALUE": raw},
                )
            self.assertEqual(caught.exception.path, ("value",))
        config = Configuration(
            "Application",
            "",
            Table(
                "limits",
                "",
                Integer("low", ""),
                Integer("high", ""),
                LessThanOrEqual("low", "high"),
            ),
        )
        with self.assertRaises(ValidationError) as caught:
            self.load_value(
                config,
                {"limits": {"low": "$LOW", "high": "$HIGH"}},
                {"LOW": "4", "HIGH": "1"},
            )
        self.assertEqual(caught.exception.path, ("limits",))
        self.assertEqual(caught.exception.constraint, "less_than_or_equal")

    def test_whole_container_references_are_rejected(self) -> None:
        schemas: tuple[Schema[Any], ...] = (
            IntegerArray("value", ""),
            NestedArray("value", "", array=IntegerArray("row", "")),
            Mapping("value", "", value=String("item", "")),
            Table("value", "", Integer("port", "")),
            TableArray("value", "", Table("item", "", Integer("port", ""))),
        )
        for schema in schemas:
            with (
                self.subTest(schema=schema),
                self.assertRaises(ValidationError) as caught,
            ):
                self.load_value(
                    Configuration("Application", "", schema),
                    {"value": "$VALUE"},
                    {"VALUE": "[1, 2]"},
                )
            self.assertEqual(caught.exception.path, ("value",))
            self.assertIn("only supported for scalar", caught.exception.detail)

    def test_defaults_and_schema_names_do_not_read_environment(self) -> None:
        config = Configuration(
            "Application",
            "",
            Integer("port", "", default=8080, optional=True),
            String("token", "", default="$TOKEN", optional=True),
            Table("server", "", Integer("port", "", default=80), optional=True),
        )
        self.assertEqual(
            self.load_value(config, {}, {"port": "9000", "TOKEN": "secret"}), {}
        )
        config = Configuration("Application", "", Integer("port", "", default=8080))
        with self.assertRaises(ValidationError) as caught:
            self.load_value(config, {}, {"port": "9000", "PORT": "9000"})
        self.assertEqual(caught.exception.path, ("port",))
        self.assertEqual(caught.exception.detail, "required table entry is missing")

    def test_normal_loading_is_unchanged(self) -> None:
        config = Configuration(
            "Application",
            "",
            String("host", ""),
            Integer("port", ""),
            Float("factor", ""),
            Boolean("debug", ""),
            LocalDate("day", ""),
        )
        values = {
            "host": "localhost",
            "port": 8080,
            "factor": 0.5,
            "debug": False,
            "day": date(2026, 10, 3),
        }
        self.assertEqual(self.load_value(config, values, {}), values)
