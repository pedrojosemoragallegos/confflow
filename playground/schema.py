from __future__ import annotations

from datetime import UTC, date, datetime, time
from pathlib import Path

from tomlkit import dumps

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

schema = Table(
    "application",
    schemas=(
        String("name"),
        Integer("version"),
        Boolean("debug"),
        LocalDate("release_date"),
        LocalTime("maintenance_time"),
        LocalDateTime("created_at"),
        OffsetDateTime("published_at"),
        StringArray("tags"),
        BooleanArray("feature_flags"),
        NestedArray("retry_schedule", array=IntegerArray("retry_window")),
        Table(
            "server",
            schemas=(
                String("host"),
                Integer("port"),
                Boolean("tls"),
            ),
        ),
        Mapping("ports", value=Integer("port")),
        TableArray(
            "backends",
            table=Table(
                "backend",
                schemas=(
                    String("name"),
                    String("url"),
                ),
            ),
        ),
    ),
)


value_model = {
    "name": "confflow",
    "version": 1,
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
