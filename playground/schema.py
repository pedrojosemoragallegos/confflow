from __future__ import annotations

import re
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Final

from tomlkit import dumps

from confflow.core.constraints.base import Constraint
from confflow.core.schemas import (
    Boolean,
    BooleanArray,
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


class Email(Constraint[str]):
    __slots__ = ()

    NAME: Final[str] = "email"

    def __call__(self, value: str, /) -> None:
        if re.fullmatch(pattern=r"[^@\s]+@[^@\s]+\.[^@\s]+", string=value) is None:
            raise ValueError("value is not a valid email address")


schema = Table(
    "application",
    "Application configuration",
    String("name", "Name of the application"),
    Integer("version", "Version of the application"),
    String("email", "Email of the application", Email()),
    Boolean("debug", "Debug mode of the application"),
    LocalDate("release_date", "Release date of the application"),
    LocalTime("maintenance_time", "Maintenance time of the application"),
    LocalDateTime("created_at", "Creation timestamp of the application"),
    OffsetDateTime("published_at", "Publication timestamp of the application"),
    StringArray("tags", "Tags associated with the application"),
    BooleanArray("feature_flags", "Feature flags of the application"),
    NestedArray(
        "retry_schedule",
        "Retry schedule of the application",
        array=IntegerArray("retry_window", "Retry window of the application"),
    ),
    Table(
        "server",
        "Server configuration",
        String("host", "Server host"),
        Integer("port", "Server port"),
        Boolean("tls", "Server TLS enabled"),
    ),
    Mapping("ports", "Mapping of ports", value=Integer("port", "Port number")),
    TableArray(
        "backends",
        "Backend servers of the application",
        Table(
            "backend",
            "Backend configuration",
            String("name", "Backend name", literal=["primary", "replica"]),
            String("url", "Backend URL"),
        ),
    ),
)


value_model = {
    "name": "confflow",
    "version": 1,
    "email": "contact@confflow.io",
    "debug": True,
    "release_date": date(2026, 10, 1),
    "maintenance_time": time(2, 30),
    "created_at": datetime.fromisoformat("2026-10-01T09:00:00"),
    "published_at": datetime(2026, 10, 1, 9, 0, tzinfo=UTC),
    "tags": ["configuration", "toml"],
    "feature_flags": [True, False, True],
    "retry_schedule": [[1, 5, 15], [30, 60]],
    "server": {
        "host": "localhost",
        "port": 8080,
        "tls": True,
    },
    "ports": {
        "http": 80,
        "https": 443,
    },
    "backends": [
        {"name": "primary", "url": "https://primary.example.com"},
        {"name": "replica", "url": "https://replica.example.com"},
    ],
}


schema.validate(value_model)
output_path = Path(__file__).with_name("application.toml")
output_path.write_text(dumps(value_model), encoding="utf-8")
print(f"Wrote {output_path}")
