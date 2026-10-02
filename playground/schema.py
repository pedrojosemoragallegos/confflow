# Ruff treats this standalone playground as a package and flags its status output.
# ruff: noqa: INP001, T201
from __future__ import annotations

import re
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Final

from confflow.renderer.markdown import MarkdownRenderer
from tomlkit import dumps

from confflow.core.definitions.constraints import Constraint
from confflow.core.schemas import (
    Boolean,
    Float,
    FloatArray,
    Integer,
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
    AtMostOneOf,
    Compare,
    RequiredTogether,
    Requires,
)


class Email(Constraint[str]):
    __slots__ = ()

    NAME: Final[str] = "email"

    def __call__(self, value: str, /) -> None:
        if (
            re.fullmatch(
                pattern=r"[^@\s]+@[^@\s]+\.[^@\s]+",
                string=value,
            )
            is None
        ):
            raise ValueError("value is not a valid email address")


schema = Table(
    "application",
    "Application configuration",
    String(
        "name",
        "Application name",
        minimum=1,
        maximum=64,
        default="confflow",
    ),
    String(
        "environment",
        "Deployment environment",
        literal=["development", "staging", "production"],
        default="production",
    ),
    String(
        "contact_email",
        "Application contact email",
        Email(),
        optional=True,
    ),
    Boolean(
        "debug",
        "Enable debug mode",
        default=False,
    ),
    LocalDate(
        "release_date",
        "Application release date",
        default=date(2026, 10, 1),
    ),
    LocalTime(
        "maintenance_time",
        "Daily maintenance time",
        default=time(2, 30),
    ),
    LocalDateTime(
        "created_at",
        "Local creation timestamp",
        default=datetime.fromisoformat("2026-10-01T09:00:00"),
    ),
    OffsetDateTime(
        "published_at",
        "Publication timestamp",
        default=datetime(2026, 10, 1, 9, 0, tzinfo=UTC),
    ),
    StringArray(
        "allowed_hosts",
        "Hosts accepted by the application",
        minimum=1,
        maximum=255,
        optional=True,
    ),
    FloatArray(
        "retry_delays",
        "Retry delays in seconds",
        minimum=0.0,
        maximum=60.0,
        optional=True,
    ),
    NestedArray(
        "clusters",
        "Groups of cluster node names",
        array=StringArray(
            "cluster",
            "Cluster node names",
            minimum=1,
            maximum=64,
        ),
        optional=True,
    ),
    Table(
        "server",
        "HTTP server configuration",
        String(
            "host",
            "Server host",
            minimum=1,
            maximum=255,
            default="localhost",
        ),
        Integer(
            "port",
            "Server port",
            minimum=1,
            maximum=65535,
            default=8080,
        ),
        Boolean(
            "tls",
            "Enable TLS",
            default=False,
        ),
        Table(
            "limits",
            "Worker limits",
            Integer(
                "minimum_workers",
                "Minimum worker count",
                minimum=1,
                maximum=128,
                default=2,
            ),
            Integer(
                "maximum_workers",
                "Maximum worker count",
                minimum=1,
                maximum=128,
                default=16,
            ),
            constraints=(
                Compare(
                    "minimum_workers",
                    "<=",
                    "maximum_workers",
                ),
            ),
        ),
    ),
    Table(
        "authentication",
        "Authentication configuration",
        String(
            "username",
            "Authentication username",
            optional=True,
        ),
        String(
            "password",
            "Authentication password",
            minimum=12,
            optional=True,
        ),
        String(
            "token",
            "Authentication token",
            optional=True,
        ),
        String(
            "certificate",
            "Client certificate",
            optional=True,
        ),
        String(
            "private_key",
            "Client private key",
            optional=True,
        ),
        optional=True,
        constraints=(
            Requires("username", "password"),
            AtMostOneOf("password", "token"),
            RequiredTogether("certificate", "private_key"),
        ),
    ),
    Mapping(
        "ports",
        "Named service ports",
        value=Integer(
            "port",
            "Port number",
            minimum=1,
            maximum=65535,
        ),
        optional=True,
    ),
    TableArray(
        "backends",
        "Backend server definitions",
        Table(
            "backend",
            "Backend configuration",
            String(
                "name",
                "Backend role",
                literal=["primary", "replica"],
            ),
            String(
                "url",
                "Backend URL",
                minimum=1,
            ),
            Float(
                "timeout",
                "Request timeout in seconds",
                minimum=0.0,
                maximum=60.0,
                default=5.0,
                optional=True,
            ),
        ),
        optional=True,
    ),
)


value_model = {
    "name": "confflow",
    "environment": "production",
    "debug": False,
    "release_date": date(2026, 10, 1),
    "maintenance_time": time(2, 30),
    "created_at": datetime.fromisoformat("2026-10-01T09:00:00"),
    "published_at": datetime(2026, 10, 1, 9, 0, tzinfo=UTC),
    "allowed_hosts": [
        "example.com",
        "api.example.com",
    ],
    "retry_delays": [
        0.5,
        1.0,
        2.0,
        5.0,
    ],
    "clusters": [
        ["node-a", "node-b"],
        ["node-c", "node-d"],
    ],
    "server": {
        "host": "localhost",
        "port": 8080,
        "tls": False,
        "limits": {
            "minimum_workers": 2,
            "maximum_workers": 16,
        },
    },
    "authentication": {
        "username": "service",
        "password": "example-secret",
    },
    "ports": {
        "http": 80,
        "https": 443,
    },
    "backends": [
        {
            "name": "primary",
            "url": "https://primary.example.com",
            "timeout": 5.0,
        },
        {
            "name": "replica",
            "url": "https://replica.example.com",
            "timeout": 10.0,
        },
    ],
}


schema.validate(value_model)

toml_path = Path(__file__).with_name("renderer-test.toml")
toml_path.write_text(dumps(value_model), encoding="utf-8")
print(f"Wrote {toml_path}")

reference = MarkdownRenderer().render(schema)

markdown_path = Path(__file__).with_name("renderer-test.md")
markdown_path.write_text(f"{reference}\n", encoding="utf-8")
print(f"Wrote {markdown_path}")
