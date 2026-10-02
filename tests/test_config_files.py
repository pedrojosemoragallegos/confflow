# These tests use unittest without adding a pytest dependency.
# ruff: noqa: PT009, PT027
from __future__ import annotations

import tomllib
import unittest
from datetime import UTC, date, datetime, time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any, cast

from confflow import Config
from confflow.core.definitions.constraints.string import (
    Length,
    String as StringConstraint,
)
from confflow.core.errors import SchemaError, ValidationError
from confflow.core.schemas import (
    Boolean,
    Float,
    Integer,
    IntegerArray,
    LocalDate,
    LocalDateTime,
    LocalTime,
    Mapping,
    NestedArray,
    OffsetDateTime,
    String,
    StringArray,
    Table,
    TableArray,
)
from confflow.core.schemas.table.constraints import (
    AtLeastOneOf,
    AtMostOneOf,
    Equal,
    ExactlyOneOf,
    Forbids,
    LessThanOrEqual,
    NotEqual,
    RequiredTogether,
    Requires,
)
from confflow.core.schemas.table.constraints.base import Constraint as TableConstraint

if TYPE_CHECKING:
    from collections.abc import Mapping as MappingABC

    from confflow.core.schemas.base import Schema
    from confflow.core.schemas.scalars.base import Scalar


class ConfigFilesTest(unittest.TestCase):
    def test_optional_subtrees_and_required_array_samples_parse(self) -> None:
        item = Table(
            "item",
            "Sample",
            String("name", "Name"),
            Float("timeout", "Timeout", default=5.0),
            Table(
                "limits",
                "Limits",
                Integer("workers", "Workers", default=2),
            ),
            Table(
                "extra", "Extra", Boolean("enabled", "", default=True), optional=True
            ),
            TableArray(
                "children",
                "Children",
                Table("child", "", String("label", "", default="child")),
            ),
        )
        config = Config(
            "Application",
            "Description",
            TableArray("active", "Active samples", item),
            TableArray("inactive", "Inactive samples", item, optional=True),
            Table(
                "monitoring",
                "Monitoring",
                Boolean("enabled", "Enabled", default=False),
                Table("nested", "Nested", Integer("port", "", default=80)),
                TableArray("samples", "Samples", item),
                optional=True,
            ),
            IntegerArray("ports", "Ports"),
            Mapping("labels", "Labels", value=String("label", "")),
        )
        with TemporaryDirectory() as directory:
            text = config.template(directory).read_text(encoding="utf-8")
            self.assertEqual(
                tomllib.loads(text),
                {
                    "active": [
                        {
                            "timeout": 5.0,
                            "limits": {"workers": 2},
                            "children": [{"label": "child"}],
                        }
                    ]
                },
            )
            for header in (
                "[[active]]",
                "[[active.children]]",
                "# [[inactive]]",
                "# [[inactive.children]]",
                "# [monitoring]",
                "# [monitoring.nested]",
                "# [[monitoring.samples]]",
            ):
                self.assertEqual(text.splitlines().count(header), 1)
            self.assertIn("# timeout = 5.0", text)
            self.assertIn("# enabled = false", text)
            self.assertIn("# port = 80", text)
            self.assertIn("# [active.extra]", text)
            self.assertIn("# name =", text)
            self.assertIn("# ports =", text)
            self.assertIn("# labels =", text)
            self.assertNotIn("# #", text)
            self.assertNotIn("\n\n\n", text)

    def test_custom_constraints_are_hidden_by_default(self) -> None:
        class HiddenField(StringConstraint):
            def __call__(self, value: str, /) -> None:
                pass

        class HiddenTable(TableConstraint):
            @property
            def fields(self) -> tuple[str, ...]:
                return ("name",)

            def __call__(self, value: MappingABC[str, object], /) -> None:
                pass

        self.assertEqual(str(HiddenField()), "")
        self.assertEqual(str(HiddenTable()), "")
        config = Config(
            "Application",
            "Description",
            Table(
                "server",
                "Server",
                String("name", "Name", HiddenField()),
                HiddenTable(),
            ),
        )
        with TemporaryDirectory() as directory:
            text = config.template(directory).read_text(encoding="utf-8")
            self.assertEqual(
                text,
                "# APPLICATION\n# Description\n\n"
                "# Server\n# Required\n[server]\n"
                "# Name\n# Required | string\n# name =\n",
            )

    def test_identity_uses_schema_name_rules(self) -> None:
        for name in ("", "not a name", "../escape"):
            with self.subTest(name=name), self.assertRaises(SchemaError):
                Config(name, "Description")
        config = Config("Application", "Application configuration")
        self.assertEqual(config.name, "Application")
        self.assertEqual(config.description, "Application configuration")

    def test_loose_fields_and_tables(self) -> None:
        field = Integer("port", "Port")
        table = Table("server", "Server", field)
        for schemas, value in (
            ((field,), {"port": 80}),
            ((table,), {"server": {"port": 80}}),
            ((table, field), {"port": 80, "server": {"port": 80}}),
        ):
            with self.subTest(schemas=schemas):
                config = Config("Application", "Description", *schemas)
                self.assertEqual(config.schemas, schemas)
                config.validate(value)
        with self.assertRaises(SchemaError):
            Config("Application", "", field, Table("port", ""))

    def test_destination_types_and_existing_directory(self) -> None:
        config = Config("Application", "Application configuration")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for destination, expected in (
                (directory, root / "application.toml"),
                (root, root / "application.toml"),
                (str(root / "production.toml"), root / "production.toml"),
                (root / "custom.conf", root / "custom.conf"),
                (root / "suffixless", root / "suffixless"),
            ):
                with self.subTest(destination=destination):
                    result = config.template(destination, overwrite=True)
                    self.assertIsInstance(result, Path)
                    self.assertEqual(result, expected)
                    self.assertEqual(
                        result.read_text(encoding="utf-8"),
                        "# APPLICATION\n# Application configuration\n\n",
                    )

    def test_parent_creation(self) -> None:
        config = Config("Application", "")
        with TemporaryDirectory() as directory:
            destination = Path(directory) / "missing" / "nested" / "prod.toml"
            with self.assertRaises(FileNotFoundError):
                config.template(destination)
            self.assertFalse(destination.parent.exists())
            self.assertEqual(config.template(destination, parents=True), destination)
            self.assertTrue(destination.is_file())

    def test_overwriting(self) -> None:
        config = Config("Application", "Description")
        with TemporaryDirectory() as directory:
            path = Path(directory) / "application.toml"
            path.write_text("original", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                config.template(path)
            self.assertEqual(path.read_text(encoding="utf-8"), "original")
            self.assertEqual(config.template(path, overwrite=True), path)
            self.assertEqual(
                path.read_text(encoding="utf-8"), "# APPLICATION\n# Description\n\n"
            )

    def test_exact_format_ordering_and_nested_tables(self) -> None:
        config = Config(
            "Application",
            "Application configuration",
            Table(
                "server",
                "Server settings",
                Table("limits", "Worker limits", Integer("workers", "Worker count")),
                Integer("port", "Server port", minimum=1, maximum=65535, default=8080),
            ),
            String("name", "Application name", default="example"),
            Table("monitoring", "Monitoring settings", optional=True),
            Boolean("debug", "Debug mode", default=False, optional=True),
        )
        expected = (
            "# APPLICATION\n# Application configuration\n\n"
            "# Application name\n"
            '# Required | string | "example"\n'
            'name = "example"\n'
            "# Debug mode\n# Optional | boolean | false\n"
            "debug = false\n\n"
            "# Server settings\n# Required\n[server]\n"
            "# Server port\n"
            "# Required | integer | 8080\n"
            "# Value must be between 1 and 65535\nport = 8080\n\n"
            "# Worker limits\n# Required\n[server.limits]\n"
            "# Worker count\n"
            "# Required | integer\n"
            "# workers =\n\n"
            "# Monitoring settings\n# Optional\n# [monitoring]\n"
        )
        with TemporaryDirectory() as directory:
            path = config.template(directory)
            text = path.read_text(encoding="utf-8")
            self.assertEqual(text, expected)
            self.assertNotIn("\n\n\n", text)
            self.assertNotIn("#", text.splitlines())
            self.assertEqual(
                tomllib.loads(text),
                {
                    "name": "example",
                    "debug": False,
                    "server": {"port": 8080, "limits": {}},
                },
            )
            with self.assertRaises(ValidationError):
                config.load(path)
            self.assertEqual(config.schemas[0].name, "server")

    def test_toml_defaults_round_trip_and_comment_safety(self) -> None:
        schemas: tuple[Scalar[Any], ...] = (
            String("message", "Multiple\nlines", default='quote "\n# [injected]'),
            Integer("count", "", default=0),
            Float("ratio", "", default=1.5),
            Boolean("flag", "", default=False),
            LocalDate("day", "", default=date(2026, 10, 2)),
            LocalTime("clock", "", default=time(2, 30)),
            LocalDateTime(
                "local", "", default=datetime.fromisoformat("2026-10-02T09:00:00")
            ),
            OffsetDateTime("offset", "", default=datetime(2026, 10, 2, tzinfo=UTC)),
        )
        config = Config("Application", "Description", *schemas)
        with TemporaryDirectory() as directory:
            text = config.template(directory).read_text(encoding="utf-8")
            parsed = tomllib.loads(text)
            self.assertEqual(
                parsed, {schema.name: schema.default for schema in schemas}
            )
            for label in (
                "integer",
                "float",
                "boolean",
                "date",
                "time",
                "local datetime",
                "offset datetime",
            ):
                self.assertIn(f"# Required | {label} | ", text)
            self.assertNotIn("default", text)

    def test_human_constraint_lines_and_blank_values(self) -> None:
        class Email(StringConstraint):
            def __call__(self, value: str, /) -> None:
                pass

        config = Config(
            "Application",
            "",
            String("email", "Contact", Email(), optional=True),
            String("code", "", Length(length=3), pattern="[A-Z]+"),
            NestedArray("groups", "", array=IntegerArray("group", "")),
            Table(
                "auth",
                "Authentication",
                String("username", "", optional=True),
                String("password", "", optional=True),
                String("token", "", optional=True),
                Requires("username", "password"),
                Forbids("password", "token"),
                AtLeastOneOf("password", "token"),
                AtMostOneOf("password", "token"),
                ExactlyOneOf("password", "token"),
                RequiredTogether("username", "password"),
                Equal("username", "password"),
                NotEqual("password", "token"),
                optional=True,
            ),
        )
        with TemporaryDirectory() as directory:
            text = config.template(directory).read_text(encoding="utf-8")
            self.assertIn("# Contact\n# Optional | string\n# email =", text)
            self.assertIn(
                '# Value must match the pattern "[A-Z]+"\n# Length must be exactly 3',
                text,
            )
            self.assertIn("# Required | array of array of integer", text)
            self.assertIn(
                "# Authentication\n# Optional\n"
                '# "username" requires "password" to be provided\n'
                '# "token" must be omitted when "password" is provided\n'
                '# At least one of "password" or "token" must be provided\n'
                '# At most one of "password" or "token" may be provided\n'
                '# Exactly one of "password" or "token" must be provided\n'
                '# "username" and "password" must be provided together\n'
                '# "username" and "password" must have equal values when provided\n'
                '# "password" and "token" must have different values when provided\n'
                "# [auth]",
                text,
            )
            for forbidden in ("type:", "constraints:", "default:", "fields=(", "None"):
                self.assertNotIn(forbidden, text)
            self.assertNotIn("\n\n\n", text)

    def test_collection_and_table_constraint_metadata(self) -> None:
        self.assertEqual(
            str(RequiredTogether("certificate", "private_key")),
            '"certificate" and "private_key" must be provided together',
        )
        self.assertEqual(
            str(RequiredTogether("first", "second", "third")),
            '"first", "second", and "third" must be provided together',
        )
        config = Config(
            "Application",
            "",
            TableArray(
                "backends",
                "Backends",
                Table("backend", "", Table("limits", "Limits", Integer("count", ""))),
                optional=True,
            ),
            IntegerArray("ports", "Ports", minimum=1),
            Mapping("labels", "Labels", value=String("label", "")),
            Table(
                "range",
                "Range",
                Integer("low", ""),
                Integer("high", ""),
                LessThanOrEqual("low", "high"),
            ),
        )
        with TemporaryDirectory() as directory:
            text = config.template(directory).read_text(encoding="utf-8")
            self.assertIn("\n# ports =\n", text)
            self.assertIn("\n# labels =\n", text)
            self.assertIn("\n# [[backends]]\n", text)
            self.assertIn("\n# [backends.limits]\n", text)
            self.assertLess(text.index("\n# ports ="), text.index("\n# [[backends]]"))
            self.assertIn(
                '# Required\n# "low" must be <= "high" when both are provided', text
            )
            self.assertIn(
                "# Required | array of integer\n# Value must be at least 1", text
            )
            self.assertIn("# Required | mapping of string", text)

    def test_constraints_use_str_and_skip_empty_strings(self) -> None:
        class Visible(StringConstraint):
            def __call__(self, value: str, /) -> None:
                pass

            def __str__(self) -> str:
                return "Use a service identifier"

            def __repr__(self) -> str:
                raise AssertionError("templates must not call repr")

        class HiddenLength(Length):
            def __str__(self) -> str:
                return ""

            def __repr__(self) -> str:
                raise AssertionError("templates must not call repr")

        class HiddenCompare(LessThanOrEqual):
            def __str__(self) -> str:
                return ""

            def __repr__(self) -> str:
                raise AssertionError("templates must not call repr")

        class VisibleCompare(LessThanOrEqual):
            def __str__(self) -> str:
                return "Keep the lower bound below the upper bound"

        table = Table(
            "limits",
            "Limits",
            Integer("low", ""),
            Integer("high", ""),
            HiddenCompare("low", "high"),
            VisibleCompare("low", "high"),
        )
        config = Config(
            "Application",
            "Description",
            String("name", "Name", Visible(), HiddenLength(minimum=1)),
            StringArray("names", "Names", HiddenLength(minimum=1)),
            table,
            TableArray("backends", "Backends", table),
        )
        with TemporaryDirectory() as directory:
            text = config.template(directory).read_text(encoding="utf-8")
            self.assertIn(
                "# Name\n# Required | string\n# Use a service identifier\n# name =",
                text,
            )
            self.assertIn("# Names\n# Required | array of string\n# names =", text)
            self.assertIn(
                "# Limits\n# Required\n"
                "# Keep the lower bound below the upper bound\n[limits]",
                text,
            )
            self.assertIn(
                "# Backends\n# Required\n"
                "# Keep the lower bound below the upper bound\n[[backends]]",
                text,
            )
            for unwanted in (
                "# length",
                "# compare",
                "internal_name",
                "\n#\n",
                "\n# \n",
            ):
                self.assertNotIn(unwanted, text)
            config.validate(
                {
                    "name": "service",
                    "names": ["service"],
                    "limits": {"low": 1, "high": 4},
                    "backends": [{"low": 1, "high": 4}],
                }
            )

    def test_literal_metadata_is_deterministic(self) -> None:
        config = Config(
            "Application",
            "Description",
            String(
                "environment",
                "Environment",
                literal=["development", "production"],
                default="production",
            ),
        )
        with TemporaryDirectory() as directory:
            path = config.template(directory)
            first = path.read_text(encoding="utf-8")
            config.template(path, overwrite=True)
            self.assertEqual(first, path.read_text(encoding="utf-8"))
            self.assertIn('# Value must be one of "development" or "production"', first)
            self.assertEqual(config.load(path), {"environment": "production"})

    def test_load_str_and_path_returns_only_user_values(self) -> None:
        config = Config(
            "Application",
            "",
            Integer("port", "", default=8080),
            String("label", "", optional=True, default="unused"),
            Table("server", "", Boolean("tls", "", default=True, optional=True)),
            Table("monitoring", "", optional=True),
        )
        with TemporaryDirectory() as directory:
            source = Path(directory) / "config.toml"
            source.write_text("port = 9000\n[server]\n", encoding="utf-8")
            for path in (source, str(source)):
                with self.subTest(path=path):
                    self.assertEqual(config.load(path), {"port": 9000, "server": {}})
            self.assertEqual(
                source.read_text(encoding="utf-8"), "port = 9000\n[server]\n"
            )

    def test_load_validation_and_relational_constraints(self) -> None:
        config = Config(
            "Application",
            "",
            Integer("port", "", default=8080, minimum=1),
            Table(
                "limits",
                "",
                Integer("low", "", default=1),
                Integer("high", "", default=4),
                LessThanOrEqual("low", "high"),
            ),
        )
        cases = (
            ("[limits]\nlow=1\nhigh=4", ("port",), None),
            ("port=0\n[limits]\nlow=1\nhigh=4", ("port",), "range"),
            ("port=80\n[limits]\nhigh=4", ("limits", "low"), None),
            ("port=80\n[limits]\nlow=4\nhigh=1", ("limits",), "less_than_or_equal"),
            ("port=80\nunknown=1\n[limits]\nlow=1\nhigh=4", ("unknown",), None),
            ("port=80\n[limits]\nlow=1\nhigh=4\nextra=5", ("limits", "extra"), None),
        )
        with TemporaryDirectory() as directory:
            source = Path(directory) / "config.toml"
            for content, path, constraint in cases:
                source.write_text(content, encoding="utf-8")
                with (
                    self.subTest(content=content),
                    self.assertRaises(ValidationError) as caught,
                ):
                    config.load(source)
                self.assertEqual(caught.exception.path, path)
                self.assertEqual(caught.exception.constraint, constraint)
            source.write_text("port=80\n[limits]\nlow=1\nhigh=4", encoding="utf-8")
            self.assertEqual(
                config.load(source), {"port": 80, "limits": {"low": 1, "high": 4}}
            )

    def test_optional_omission_and_standard_errors(self) -> None:
        config = Config(
            "Application", "", Integer("port", "", optional=True, default=8080)
        )
        with TemporaryDirectory() as directory:
            source = Path(directory) / "config.toml"
            with self.assertRaises(FileNotFoundError):
                config.load(source)
            source.write_text("", encoding="utf-8")
            self.assertEqual(config.load(source), {})
            source.write_text("port = [", encoding="utf-8")
            with self.assertRaises(tomllib.TOMLDecodeError):
                config.load(source)
            source.write_text('port = "wrong"', encoding="utf-8")
            with self.assertRaises(ValidationError):
                config.load(source)
            with self.assertRaises(SchemaError):
                Config("Application", "", cast("Schema[Any]", object()))
