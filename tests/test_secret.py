# These tests use unittest without adding a pytest dependency.
# ruff: noqa: PT009, PT027, S105
from __future__ import annotations

import os
import traceback
import unittest
from datetime import UTC, date, datetime, time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, cast
from unittest.mock import patch

import tomlkit

from confflow import Configuration
from confflow.core.definitions.constraints.string import String as StringConstraint
from confflow.core.errors import ValidationError
from confflow.core.schemas import (
    Boolean,
    Float,
    Integer,
    LocalDate,
    LocalDateTime,
    LocalTime,
    Mapping,
    NestedArray,
    OffsetDateTime,
    String,
    Table,
    TableArray,
)
from confflow.core.schemas.table.constraints import Equal

if TYPE_CHECKING:
    from collections.abc import Mapping as MappingABC


class RejectValue(StringConstraint):
    def __call__(self, value: str, /) -> None:
        raise ValueError(f"rejected input {value!r}")


class SecretTest(unittest.TestCase):
    def load_value(
        self,
        config: Configuration,
        value: MappingABC[str, object],
        environment: MappingABC[str, str] | None = None,
    ) -> MappingABC[str, object]:
        with (
            TemporaryDirectory() as directory,
            patch.dict(os.environ, environment or {}, clear=True),
        ):
            source = Path(directory) / "config.toml"
            source.write_text(tomlkit.dumps(dict(value)), encoding="utf-8")
            return config.load(source)

    def template(self, config: Configuration) -> str:
        with TemporaryDirectory() as directory:
            return config.template(directory).read_text(encoding="utf-8")

    def assert_redacted(self, error: ValidationError, secret: str) -> None:
        diagnostics = (
            str(error),
            repr(error),
            repr(error.args),
            repr(error.value),
            error.detail,
            str(error.expected),
            "".join(traceback.format_exception(error)),
        )
        for diagnostic in diagnostics:
            self.assertNotIn(secret, diagnostic)
        self.assertIn("<secret>", repr(error.value))

    def test_secret_defaults_to_false_for_all_scalars(self) -> None:
        for scalar in (
            String,
            Boolean,
            Integer,
            Float,
            LocalDate,
            LocalTime,
            LocalDateTime,
            OffsetDateTime,
        ):
            with self.subTest(scalar=scalar):
                self.assertFalse(scalar("value", "").secret)
                self.assertTrue(scalar("value", "", secret=True).secret)

    def test_secret_string_loads_real_literal_and_environment_values(self) -> None:
        field = String("password", "Database password", optional=True, secret=True)
        self.assertEqual(field.name, "password")
        self.assertTrue(field.optional)
        config = Configuration("Application", "", field)
        for value in ("literal-password", "$DB_PASSWORD"):
            with self.subTest(value=value):
                loaded = self.load_value(
                    config, {"password": value}, {"DB_PASSWORD": "resolved-password"}
                )
                expected = "resolved-password" if value == "$DB_PASSWORD" else value
                self.assertEqual(loaded["password"], expected)
                self.assertEqual(loaded, {"password": expected})
                self.assertNotIn(expected, repr(loaded))
                self.assertNotIn(expected, str(loaded))
                self.assertIn("password", repr(loaded))
                self.assertIn("<secret>", repr(loaded))
                with self.assertRaises(TypeError):
                    cast("dict[str, object]", loaded)["password"] = "changed"
        self.assertEqual(self.load_value(config, {}), {})
        self.assertEqual(
            self.load_value(config, {"password": "$$DB_PASSWORD"})["password"],
            "$DB_PASSWORD",
        )

    def test_secret_scalar_conversions_do_not_change(self) -> None:
        cases = (
            (Boolean, "true", True),
            (Integer, "8080", 8080),
            (Float, "0.5", 0.5),
            (LocalDate, "2026-10-03", date(2026, 10, 3)),
            (LocalTime, "12:34:56", time(12, 34, 56)),
            (
                LocalDateTime,
                "2026-10-03T12:34:56",
                datetime(2026, 10, 3, 12, 34, 56),  # noqa: DTZ001
            ),
            (
                OffsetDateTime,
                "2026-10-03T12:34:56Z",
                datetime(2026, 10, 3, 12, 34, 56, tzinfo=UTC),
            ),
        )
        for scalar, raw, expected in cases:
            with self.subTest(scalar=scalar):
                loaded = self.load_value(
                    Configuration("Application", "", scalar("value", "", secret=True)),
                    {"value": "$VALUE"},
                    {"VALUE": raw},
                )
                self.assertEqual(loaded["value"], expected)
                self.assertIs(type(loaded["value"]), type(expected))
                self.assertIn("<secret>", repr(loaded))

    def test_validation_error_redacts_value_and_keeps_path_and_constraint(self) -> None:
        secret = "short-password"
        field = String("password", "", secret=True, minimum=50)
        with self.assertRaises(ValidationError) as caught:
            self.load_value(
                Configuration("Application", "", Table("database", "", field)),
                {"database": {"password": "$PASSWORD"}},
                {"PASSWORD": secret},
            )
        error = caught.exception
        self.assertEqual(error.path, ("database", "password"))
        self.assertEqual(error.constraint, "length")
        self.assertEqual(error.value, "<secret>")
        self.assertIn("database.password", str(error))
        self.assertIn("shorter than the minimum length", error.detail)
        self.assert_redacted(error, secret)

    def test_custom_constraint_error_redacts_message_args_and_traceback(self) -> None:
        secret = "rejected-password"
        field = String("password", "", RejectValue(), secret=True)
        with self.assertRaises(ValidationError) as caught:
            field.validate(secret)
        self.assert_redacted(caught.exception, secret)
        self.assertEqual(caught.exception.constraint, "reject_value")
        self.assertIn("rejected input", caught.exception.detail)
        self.assertIsNone(caught.exception.__cause__)
        with self.assertRaises(ValidationError) as caught:
            self.load_value(
                Configuration("Application", "", field),
                {"password": "$PASSWORD"},
                {"PASSWORD": secret},
            )
        self.assert_redacted(caught.exception, secret)
        self.assertEqual(caught.exception.path, ("password",))
        self.assertEqual(caught.exception.constraint, "reject_value")
        self.assertIn("rejected input", caught.exception.detail)
        try:
            field.validate(secret)
        except ValidationError as error:
            self.assert_redacted(error, secret)
        else:
            self.fail("secret metadata must not disable custom validation")

    def test_literal_errors_do_not_expose_secret_defaults_or_allowed_values(
        self,
    ) -> None:
        field = String(
            "password",
            "",
            default="allowed-password",
            literal=["allowed-password", "alternate-password"],
            secret=True,
        )
        with self.assertRaises(ValidationError) as caught:
            field.validate("wrong-password")
        for value in ("wrong-password", "allowed-password", "alternate-password"):
            self.assert_redacted(caught.exception, value)
        self.assertEqual(caught.exception.constraint, "literal")
        self.assertIn("value must be one of", caught.exception.detail)

    def test_default_validation_is_unchanged_but_redacted(self) -> None:
        with self.assertRaises(ValidationError) as caught:
            String("password", "", default="invalid-password", minimum=50, secret=True)
        self.assertEqual(caught.exception.path, ("password",))
        self.assertEqual(caught.exception.constraint, "length")
        self.assert_redacted(caught.exception, "invalid-password")

    def test_environment_failures_are_redacted(self) -> None:
        config = Configuration("Application", "", Integer("pin", "", secret=True))
        with self.assertRaises(ValidationError) as caught:
            self.load_value(config, {"pin": "$PIN"}, {"PIN": "invalid-secret-pin"})
        self.assert_redacted(caught.exception, "invalid-secret-pin")
        self.assertNotIn("$PIN", repr(caught.exception.value))
        self.assertEqual(caught.exception.path, ("pin",))
        self.assertIn("PIN", caught.exception.detail)
        self.assertIn("cannot be converted", caught.exception.detail)
        with self.assertRaises(ValidationError) as caught:
            self.load_value(config, {"pin": "$PIN"})
        self.assertEqual(caught.exception.path, ("pin",))
        self.assertEqual(caught.exception.value, "<secret>")
        self.assertIn("PIN", str(caught.exception))
        self.assertIn("not set", caught.exception.detail)

    def test_repr_hides_default_and_preserves_schema_metadata(self) -> None:
        field = String(
            "password",
            "Database password",
            default="default-password",
            literal=["default-password"],
            secret=True,
        )
        for represented in (
            field,
            Table("database", "", field),
            Mapping("passwords", "", value=field),
            TableArray("databases", "", Table("database", "", field)),
        ):
            self.assertNotIn("default-password", repr(represented))
            self.assertIn("password", repr(represented))
            self.assertIn("<secret>", repr(represented))
        self.assertEqual(field.default, "default-password")

    def test_template_marks_secrets_and_never_renders_defaults(self) -> None:
        config = Configuration(
            "Application",
            "",
            String(
                "password", "Database password", default="default-password", secret=True
            ),
            String("token", "", optional=True, default="default-token", secret=True),
            String("host", "", default="localhost"),
        )
        text = self.template(config)
        self.assertIn(
            "# Database password\n# Required | string | secret\npassword =\n", text
        )
        self.assertIn("# Optional | string | secret\ntoken =\n", text)
        self.assertNotIn("default-password", text)
        self.assertNotIn("default-token", text)
        self.assertNotIn("$PASSWORD", text)
        self.assertIn('# Required | string | "localhost"\nhost = "localhost"', text)

    def test_nested_templates_and_loaded_representations_redact_secrets(self) -> None:
        field = String(
            "password",
            "",
            default="container-password",
            literal=["container-password"],
            secret=True,
        )
        table = Table("database", "", field)
        config = Configuration(
            "Application",
            "",
            Table("server", "", field),
            Mapping("passwords", "", value=field),
            Mapping("databases", "", value=table),
            TableArray("backends", "", table),
            NestedArray("groups", "", array=TableArray("items", "", table)),
        )
        text = self.template(config)
        self.assertNotIn("container-password", text)
        self.assertIn("# # Required | string | secret", text)
        self.assertIn("# <key> =\n", text)
        loaded = self.load_value(
            config,
            {
                "server": {"password": "container-password"},
                "passwords": {"primary": "container-password"},
                "databases": {"primary": {"password": "container-password"}},
                "backends": [{"password": "container-password"}],
                "groups": [[{"password": "container-password"}]],
            },
        )
        self.assertNotIn("container-password", repr(loaded))
        self.assertIn("<secret>", repr(loaded))
        passwords = cast("MappingABC[str, object]", loaded["passwords"])
        self.assertEqual(passwords["primary"], "container-password")

    def test_relational_errors_redact_only_secret_values(self) -> None:
        table = Table(
            "credentials",
            "",
            String("password", "", secret=True),
            String("confirmation", ""),
            Equal("password", "confirmation"),
        )
        with self.assertRaises(ValidationError) as caught:
            self.load_value(
                Configuration("Application", "", table),
                {
                    "credentials": {
                        "password": "relational-password",
                        "confirmation": "public-value",
                    }
                },
            )
        error = caught.exception
        self.assert_redacted(error, "relational-password")
        self.assertEqual(error.path, ("credentials",))
        self.assertEqual(error.constraint, "equal")
        self.assertEqual(
            error.value, {"password": "<secret>", "confirmation": "public-value"}
        )
        self.assertIn("password", str(error))
        self.assertIn("confirmation", str(error))

    def test_relational_errors_redact_nested_secret_values(self) -> None:
        table = Table(
            "credentials",
            "",
            Table("first", "", String("password", "", secret=True)),
            Table("second", "", String("password", "", secret=True)),
            Equal("first", "second"),
        )
        with self.assertRaises(ValidationError) as caught:
            table.validate(
                {
                    "first": {"password": "first-secret-password"},
                    "second": {"password": "second-secret-password"},
                }
            )
        self.assert_redacted(caught.exception, "first-secret-password")
        self.assert_redacted(caught.exception, "second-secret-password")
        self.assertEqual(
            caught.exception.value,
            {"first": {"password": "<secret>"}, "second": {"password": "<secret>"}},
        )

    def test_nonsecret_diagnostics_defaults_and_required_behavior_unchanged(
        self,
    ) -> None:
        field = String("password", "", default="ordinary-default", minimum=10)
        self.assertIn("ordinary-default", repr(field))
        self.assertIn(
            'password = "ordinary-default"',
            self.template(Configuration("Application", "", field)),
        )
        with self.assertRaises(ValidationError) as caught:
            field.validate("short")
        self.assertEqual(caught.exception.value, "short")
        self.assertIn("short", str(caught.exception))
        config = Configuration(
            "Application", "", String("password", "", secret=True, default="unused")
        )
        with self.assertRaises(ValidationError) as caught:
            self.load_value(config, {})
        self.assertEqual(caught.exception.path, ("password",))
        self.assertEqual(caught.exception.detail, "required table entry is missing")
        self.assertEqual(
            self.load_value(
                Configuration(
                    "Application",
                    "",
                    String(
                        "password", "", secret=True, optional=True, default="unused"
                    ),
                ),
                {},
            ),
            {},
        )
