# These tests use unittest without adding a pytest dependency.
# ruff: noqa: PT009, PT027
from __future__ import annotations

import tomllib
import unittest
from datetime import UTC, date, datetime, time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any, cast

import tomlkit

from confflow import Configuration
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
    def load_value(
        self,
        config: Configuration,
        value: MappingABC[str, object],
    ) -> MappingABC[str, object]:
        with TemporaryDirectory() as directory:
            source = Path(directory) / "config.toml"
            source.write_text(tomlkit.dumps(dict(value)), encoding="utf-8")
            return config.load(source)

    def test_assignment_presence_and_spacing(self) -> None:
        fields = (
            Integer("required_value", "", default=0),
            String("required_blank", ""),
            Boolean("optional_value", "", default=False, optional=True),
            String("optional_blank", "", optional=True),
        )
        config = Configuration(
            "Application",
            "Description",
            *fields,
            Table("settings", "Settings", *fields),
            TableArray("items", "Items", Table("item", "", *fields), optional=True),
            Table("disabled", "Disabled", *fields, optional=True),
        )
        assignments = (
            "# Required | integer | 0\nrequired_value = 0\n"
            "# Required | string\nrequired_blank =\n"
            "# Optional | boolean | false\noptional_value = false\n"
            "# Optional | string\noptional_blank ="
        )
        with TemporaryDirectory() as directory:
            text = config.template(directory).read_text(encoding="utf-8")
        self.assertEqual(text.count(assignments), 3)
        self.assertIn(assignments + "\n\n# Settings", text)
        self.assertIn("[settings]\n" + assignments, text)
        commented_assignments = "\n".join(
            f"# {line}" for line in assignments.splitlines()
        )
        self.assertIn(
            "# [[items]]\n" + commented_assignments + "\n# --- </copy block> ---", text
        )
        self.assertIn("# --- </copy block> ---\n\n# Disabled", text)
        self.assertIn("[disabled]\n" + assignments, text)
        self.assertIn(
            "# Optional | array of tables\n"
            "# --- <copy block> ---",
            text,
        )
        self.assertNotIn("\n\n\n", text)

    def test_repeatable_sample_exact_format(self) -> None:
        item = Table(
            "backend",
            "Backend",
            String("name", "Backend role", literal=["primary", "replica"]),
            String("url", "Backend URL", minimum=1),
            Float(
                "timeout",
                "Request timeout in seconds",
                default=5.0,
                minimum=0.0,
                maximum=60.0,
                optional=True,
            ),
        )
        for optional in (True, False):
            config = Configuration(
                "Application",
                "Description",
                Table(
                    "application",
                    "",
                    TableArray(
                        "backends",
                        "Backend server definitions",
                        item,
                        optional=optional,
                    ),
                ),
            )
            with TemporaryDirectory() as directory:
                text = config.template(directory).read_text(encoding="utf-8")
                requirement = "Optional" if optional else "Required"
                expected = (
                    "# Backend server definitions\n"
                    f"# {requirement} | array of tables\n"
                    "# --- <copy block> ---\n"
                    "# [[application.backends]]\n"
                    "# # Backend role\n# # Required | string\n"
                    '# # Value must be one of "primary" or "replica"\n# name =\n'
                    "# # Backend URL\n# # Required | string\n"
                    "# # Length must be at least 1\n# url =\n"
                    "# # Request timeout in seconds\n# # Optional | float | 5.0\n"
                    "# # Value must be between 0.0 and 60.0\n# timeout = 5.0\n"
                    "# --- </copy block> ---\n"
                )
                self.assertTrue(text.endswith(expected))
                self.assertEqual(text.count("# --- <copy block>"), 1)
                self.assertEqual(text.count("# --- </copy block> ---"), 1)
                self.assertEqual(tomllib.loads(text), {"application": {}})
                block = text.split("# --- <copy block> ---\n", 1)[1].split(
                    "# --- </copy block> ---", 1
                )[0]
                uncommented = (
                    "\n".join(line.removeprefix("# ") for line in block.splitlines())
                    + "\n"
                )
                self.assertIn("# Backend role\n# Required | string\n", uncommented)
                completed = uncommented.replace(
                    "name =\n", 'name = "primary"\n'
                ).replace("url =\n", 'url = "https://example.com"\n')
                self.assertEqual(
                    tomllib.loads(completed),
                    {
                        "application": {
                            "backends": [
                                {
                                    "name": "primary",
                                    "url": "https://example.com",
                                    "timeout": 5.0,
                                }
                            ]
                        }
                    },
                )
                self.load_value(config, tomllib.loads(completed))
                self.assertNotIn("\n\n\n", text)

    def test_repeatable_samples_are_commented_in_optional_subtrees(self) -> None:
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
        config = Configuration(
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
            for header in (
                "# [[active]]",
                "# # [[active.children]]",
                "# [[inactive]]",
                "# # [[inactive.children]]",
                "[monitoring]",
                "[monitoring.nested]",
                "# [[monitoring.samples]]",
            ):
                self.assertEqual(text.splitlines().count(header), 1)
            self.assertEqual(text.splitlines().count("# timeout = 5.0"), 3)
            self.assertEqual(text.splitlines().count("# [active.limits]"), 1)
            self.assertEqual(text.splitlines().count("# workers = 2"), 3)
            self.assertEqual(text.splitlines().count('# # label = "child"'), 3)
            self.assertEqual(text.count("# --- <copy block> ---"), 7)
            self.assertEqual(text.count("# --- </copy block> ---"), 7)
            self.assertIn("\nenabled = false\n", text)
            self.assertIn("\nport = 80\n", text)
            self.assertIn("\n# [active.extra]\n", text)
            self.assertEqual(text.splitlines().count("# enabled = true"), 3)
            self.assertEqual(text.splitlines().count("# name ="), 3)
            self.assertIn("\nports =\n", text)
            self.assertIn("\n[labels]\n", text)
            self.assertIn("\n# <key> =\n", text)
            self.assertIn("timeout = 5.0\n\n# # Limits", text)
            self.assertIn("# [active.limits]\n# # Workers", text)
            self.assertNotIn("\n\n\n", text)

    def test_mapping_samples_for_scalar_and_table_values(self) -> None:
        config = Configuration(
            "Application",
            "Description",
            Mapping(
                "ports",
                "Named service ports",
                value=Integer("port", "Port number", minimum=1, default=8080),
            ),
            Mapping(
                "backends",
                "Named backend configurations",
                value=Table(
                    "backend",
                    "Backend configuration",
                    String("name", "Backend name", default="primary"),
                    Integer("minimum_workers", "Minimum workers", default=1),
                    Integer("maximum_workers", "Maximum workers", default=4),
                    LessThanOrEqual("minimum_workers", "maximum_workers"),
                ),
            ),
        )
        with TemporaryDirectory() as directory:
            text = config.template(directory).read_text(encoding="utf-8")

        self.assertIn(
            "# Named service ports\n"
            "# Required | table\n"
            "[ports]\n"
            "# --- <copy block> ---\n"
            "# # Port number\n"
            "# # Required | integer | 8080\n"
            "# # Value must be at least 1\n"
            "# <key> = 8080\n"
            "# --- </copy block> ---",
            text,
        )
        self.assertIn(
            "# Named backend configurations\n"
            "# Required | table\n"
            "[backends]\n"
            "# --- <copy block> ---\n"
            "# # Backend configuration\n"
            "# # Required\n"
            '# # "minimum_workers" must be <= "maximum_workers"\n'
            "# [backends.<key>]\n"
            "# # Backend name\n"
            '# # Required | string | "primary"\n'
            '# name = "primary"\n'
            "# # Minimum workers\n"
            "# # Required | integer | 1\n"
            "# minimum_workers = 1\n"
            "# # Maximum workers\n"
            "# # Required | integer | 4\n"
            "# maximum_workers = 4\n"
            "# --- </copy block> ---",
            text,
        )
        self.assertIn(
            '# "minimum_workers" must be <= "maximum_workers"',
            text,
        )
        self.assertEqual(
            tomllib.loads(text),
            {"ports": {}, "backends": {}},
        )

        uncommented = list(text.splitlines())
        index = 0
        while index < len(uncommented):
            if uncommented[index] != "# --- <copy block> ---":
                index += 1
                continue
            end = uncommented.index("# --- </copy block> ---", index + 1)
            uncommented[index : end + 1] = [
                line.removeprefix("# ").replace("<key>", "sample")
                for line in uncommented[index + 1 : end]
            ]
        values = tomllib.loads("\n".join(uncommented))
        self.assertEqual(
            values,
            {
                "ports": {"sample": 8080},
                "backends": {
                    "sample": {
                        "name": "primary",
                        "minimum_workers": 1,
                        "maximum_workers": 4,
                    }
                },
            },
        )
        self.load_value(config, values)

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
        config = Configuration(
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
                "# Description\n\n"
                "# Server\n# Required\n[server]\n"
                "# Name\n# Required | string\nname =\n",
            )

    def test_identity_uses_schema_name_rules(self) -> None:
        for name in ("", "not a name", "../escape"):
            with self.subTest(name=name), self.assertRaises(SchemaError):
                Configuration(name, "Description")
        Configuration("Application", "Application configuration")

    def test_loose_fields_and_tables(self) -> None:
        field = Integer("port", "Port")
        table = Table("server", "Server", field)
        for schemas, value in (
            ((field,), {"port": 80}),
            ((table,), {"server": {"port": 80}}),
            ((table, field), {"port": 80, "server": {"port": 80}}),
        ):
            with self.subTest(schemas=schemas):
                config = Configuration("Application", "Description", *schemas)
                self.load_value(config, value)
        with self.assertRaises(SchemaError):
            Configuration("Application", "", field, Table("port", ""))

    def test_destination_types_and_existing_directory(self) -> None:
        config = Configuration("Application", "Application configuration")
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
                        "# Application configuration\n\n",
                    )

    def test_parent_creation(self) -> None:
        config = Configuration("Application", "")
        with TemporaryDirectory() as directory:
            destination = Path(directory) / "missing" / "nested" / "prod.toml"
            with self.assertRaises(FileNotFoundError):
                config.template(destination)
            self.assertFalse(destination.parent.exists())
            self.assertEqual(config.template(destination, parents=True), destination)
            self.assertTrue(destination.is_file())

    def test_overwriting(self) -> None:
        config = Configuration("Application", "Description")
        with TemporaryDirectory() as directory:
            path = Path(directory) / "application.toml"
            path.write_text("original", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                config.template(path)
            self.assertEqual(path.read_text(encoding="utf-8"), "original")
            self.assertEqual(config.template(path, overwrite=True), path)
            self.assertEqual(
                path.read_text(encoding="utf-8"), "# Description\n\n"
            )

    def test_exact_format_ordering_and_nested_tables(self) -> None:
        config = Configuration(
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
            "# Application configuration\n\n"
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
            "workers =\n\n"
            "# Monitoring settings\n# Optional\n[monitoring]\n"
        )
        with TemporaryDirectory() as directory:
            path = config.template(directory)
            text = path.read_text(encoding="utf-8")
            self.assertEqual(text, expected)
            self.assertNotIn("\n\n\n", text)
            self.assertNotIn("#", text.splitlines())
            self.assertEqual(
                tomllib.loads(text.replace("workers =\n", "workers = 2\n")),
                {
                    "name": "example",
                    "debug": False,
                    "server": {"port": 8080, "limits": {"workers": 2}},
                    "monitoring": {},
                },
            )
            with self.assertRaises(tomllib.TOMLDecodeError):
                config.load(path)

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
        config = Configuration("Application", "Description", *schemas)
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
                "local date",
                "local time",
                "local date-time",
                "offset date-time",
            ):
                self.assertIn(f"# Required | {label} | ", text)
            self.assertNotIn("default", text)

    def test_human_constraint_lines_and_blank_values(self) -> None:
        class Email(StringConstraint):
            def __call__(self, value: str, /) -> None:
                pass

        config = Configuration(
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
            self.assertIn("# Contact\n# Optional | string\nemail =", text)
            self.assertIn(
                '# Value must match the pattern "[A-Z]+"\n# Length must be exactly 3',
                text,
            )
            self.assertIn("# Required | array of array of integer", text)
            self.assertIn(
                "# Authentication\n# Optional\n"
                '# When "username" is provided, "password" must also be provided\n'
                '# When "password" is provided, "token" must be omitted\n'
                '# Either "password" or "token" must be provided; '
                "both may be provided\n"
                '# Either "password" or "token" may be provided, but not both\n'
                '# Either "password" or "token", but not both, must be provided\n'
                '# When either "username" or "password" is provided, '
                "both must be provided\n"
                '# "username" == "password"\n'
                '# "password" != "token"\n'
                "[auth]",
                text,
            )
            for forbidden in ("type:", "constraints:", "default:", "fields=(", "None"):
                self.assertNotIn(forbidden, text)
            self.assertNotIn("\n\n\n", text)

    def test_collection_and_table_constraint_metadata(self) -> None:
        self.assertEqual(
            str(RequiredTogether("certificate", "private_key")),
            'When either "certificate" or "private_key" is provided, '
            "both must be provided",
        )
        self.assertEqual(
            str(RequiredTogether("first", "second", "third")),
            'When any of "first", "second", or "third" is provided, '
            "all of them must be provided",
        )
        config = Configuration(
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
            self.assertIn("\nports =\n", text)
            self.assertIn("\n[labels]\n", text)
            self.assertIn("\n# <key> =\n", text)
            self.assertIn("\n# [[backends]]\n", text)
            self.assertIn("\n# [backends.limits]\n", text)
            self.assertIn("\n# count =\n", text)
            self.assertLess(text.index("\nports ="), text.index("\n# [[backends]]"))
            self.assertIn(
                '# Required\n# "low" must be <= "high"',
                text,
            )
            self.assertIn(
                "# Required | array of integer\n# Value must be at least 1", text
            )
            self.assertIn("# Required | table", text)

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
        config = Configuration(
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
                "# Name\n# Required | string\n# Use a service identifier\nname =",
                text,
            )
            self.assertIn("# Names\n# Required | array of string\nnames =", text)
            self.assertIn(
                "# Limits\n# Required\n"
                "# Keep the lower bound below the upper bound\n[limits]",
                text,
            )
            self.assertIn(
                "# Backends\n# Required | array of tables\n"
                "# --- <copy block> ---\n# [[backends]]\n"
                "# # Keep the lower bound below the upper bound",
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
            self.load_value(
                config,
                {
                    "name": "service",
                    "names": ["service"],
                    "limits": {"low": 1, "high": 4},
                    "backends": [{"low": 1, "high": 4}],
                }
            )

    def test_literal_metadata_is_deterministic(self) -> None:
        config = Configuration(
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
        config = Configuration(
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

    def test_load_returns_deeply_immutable_values(self) -> None:
        config = Configuration(
            "Application",
            "",
            StringArray("tags", ""),
            Table("server", "", StringArray("hosts", "")),
            Mapping("labels", "", value=String("label", "")),
        )
        with TemporaryDirectory() as directory:
            source = Path(directory) / "config.toml"
            source.write_text(
                'tags = ["stable"]\n'
                '[server]\n'
                'hosts = ["localhost"]\n'
                '[labels]\n'
                'environment = "production"\n',
                encoding="utf-8",
            )
            value = config.load(source)

        with self.assertRaises(TypeError):
            cast("dict[str, object]", value)["new"] = "value"

        server = cast("Mapping[str, object]", value["server"])
        hosts = cast("tuple[str, ...]", server["hosts"])
        self.assertEqual(hosts, ("localhost",))
        with self.assertRaises(TypeError):
            cast("dict[str, object]", server)["new"] = "value"

        labels = cast("Mapping[str, object]", value["labels"])
        self.assertEqual(labels["environment"], "production")
        self.assertEqual(value["tags"], ("stable",))

    def test_load_validation_and_relational_constraints(self) -> None:
        config = Configuration(
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
        config = Configuration(
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
                Configuration("Application", "", cast("Schema[Any]", object()))
