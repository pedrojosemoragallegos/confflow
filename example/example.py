from __future__ import annotations

import re
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Final

from confflow import Configuration
from confflow.constraints import (
    AtLeastOneOf,
    AtMostOneOf,
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
    StringConstraint,
)
from confflow.schemas import (
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


class Email(StringConstraint):
    __slots__ = ()

    def __call__(self, value: str, /) -> None:
        if re.fullmatch(pattern=r"[^@\s]+@[^@\s]+\.[^@\s]+", string=value) is None:
            raise ValueError("value is not a valid email address")


def create_config() -> Configuration:
    limits: Table = Table(
        "limits",
        "Worker limits",
        Integer(
            "minimum_workers", "Minimum worker count", minimum=1, maximum=128, default=2
        ),
        Integer(
            "maximum_workers",
            "Maximum worker count",
            minimum=1,
            maximum=128,
            default=16,
        ),
        LessThanOrEqual("minimum_workers", "maximum_workers"),
    )

    server: Table = Table(
        "server",
        "HTTP server configuration",
        String("host", "Server host", minimum=1, maximum=255, default="localhost"),
        Integer("port", "Server port", minimum=1, maximum=65535, default=8080),
        Boolean("tls", "TLS mode", default=False),
        limits,
    )

    less_than_example: Table = Table(
        "less_than",
        "Strictly increasing values",
        Integer("smaller", None, default=1),
        Integer("larger", None, default=2),
        LessThan("smaller", "larger"),
    )

    less_than_or_equal_example: Table = Table(
        "less_than_or_equal",
        "Increasing or equal values",
        Integer("lower", None, default=2),
        Integer("upper", None, default=2),
        LessThanOrEqual("lower", "upper"),
    )

    greater_than_example: Table = Table(
        "greater_than",
        "Strictly decreasing values",
        Integer("larger", None, default=2),
        Integer("smaller", None, default=1),
        GreaterThan("larger", "smaller"),
    )

    greater_than_or_equal_example: Table = Table(
        "greater_than_or_equal",
        "Decreasing or equal values",
        Integer("left", None, default=2),
        Integer("right", None, default=2),
        GreaterThanOrEqual("left", "right"),
    )

    comparison_examples: Table = Table(
        "comparison_examples",
        "Examples of ordered comparison constraints",
        less_than_example,
        less_than_or_equal_example,
        greater_than_example,
        greater_than_or_equal_example,
    )

    authentication: Table = Table(
        "authentication",
        "Authentication configuration",
        String("username", "Authentication username", optional=True),
        String(
            "password",
            "Authentication password",
            minimum=12,
            optional=True,
            secret=True,
        ),
        String("token", "Authentication token", optional=True, secret=True),
        String("certificate", "Client certificate", optional=True),
        String("private_key", "Client private key", optional=True, secret=True),
        Requires("username", "password"),
        AtMostOneOf("password", "token"),
        RequiredTogether("certificate", "private_key"),
        optional=True,
    )

    notifications: Table = Table(
        "notifications",
        "Notification delivery",
        String("email", "Notification email address", optional=True),
        String("webhook", "Notification webhook URL", optional=True),
        AtLeastOneOf("email", "webhook"),
    )

    storage: Table = Table(
        "storage",
        "Storage backend selection",
        String("local_path", "Local storage directory", optional=True),
        String("bucket", "Cloud storage bucket", optional=True),
        String("region", "Cloud storage region", optional=True),
        ExactlyOneOf("local_path", "bucket"),
        Forbids("local_path", "region"),
    )

    replication: Table = Table(
        "replication",
        "Replication compatibility and identity",
        String("primary_protocol", "Primary replication protocol"),
        String("replica_protocol", "Replica replication protocol"),
        String("primary_id", "Primary node identifier"),
        String("replica_id", "Replica node identifier"),
        Equal("primary_protocol", "replica_protocol"),
        NotEqual("primary_id", "replica_id"),
    )

    service_config: Table = Table(
        "service",
        "Service configuration",
        String("url", "Service URL", minimum=1),
        Integer("weight", "Traffic weight", minimum=1, default=1),
    )

    services: Mapping = Mapping(
        "services", "Named service configurations", value=service_config, optional=True
    )

    ports: Mapping = Mapping(
        "ports",
        "Named service ports",
        value=Integer("port", "Port number", minimum=1, maximum=65535),
        optional=True,
    )

    backend: Table = Table(
        "backend",
        "Backend configuration",
        String("name", "Backend role", literal=["primary", "replica"]),
        String("url", "Backend URL", minimum=1),
        Float(
            "timeout",
            "Request timeout in seconds",
            minimum=0.0,
            maximum=60.0,
            default=5.0,
            optional=True,
        ),
    )

    backends: TableArray = TableArray(
        "backends", "Backend server definitions", backend, optional=True
    )

    monitoring: Table = Table(
        "monitoring",
        "Application monitoring",
        String("endpoint", "Monitoring endpoint", minimum=1),
        optional=True,
    )

    application: Table = Table(
        "application",
        "Application configuration",
        String("name", "Application name", minimum=1, maximum=64, default="confflow"),
        String(
            "environment",
            "Deployment environment",
            literal=["development", "staging", "production"],
            default="production",
        ),
        String("contact_email", "Application contact email", Email(), optional=True),
        Boolean("debug", "Debug mode", default=False),
        Float(
            "load_factor", "Current load factor", minimum=0.0, maximum=1.0, default=0.5
        ),
        LocalDate(
            "release_date",
            "Application release date",
            default=date(year=2026, month=10, day=2),
        ),
        LocalTime(
            "maintenance_time",
            "Daily maintenance time",
            default=time(hour=2, minute=30),
        ),
        LocalDateTime(
            "created_at",
            "Local creation timestamp",
            default=datetime.fromisoformat("2026-10-02T09:00:00"),
        ),
        OffsetDateTime(
            "published_at",
            "Publication timestamp",
            default=datetime(year=2026, month=10, day=2, hour=9, minute=0, tzinfo=UTC),
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
        BooleanArray("feature_flags", "Enabled feature flags", optional=True),
        IntegerArray(
            "retry_codes",
            "Retryable response codes",
            minimum=100,
            maximum=599,
            optional=True,
        ),
        LocalDateArray(
            "maintenance_dates", "Scheduled maintenance dates", optional=True
        ),
        LocalTimeArray("quiet_hours", "Daily quiet-hour start times", optional=True),
        LocalDateTimeArray(
            "scheduled_checks", "Scheduled local health checks", optional=True
        ),
        OffsetDateTimeArray(
            "audit_timestamps", "Offset-aware audit timestamps", optional=True
        ),
        NestedArray(
            "clusters",
            "Groups of cluster node names",
            array=StringArray("cluster", "Cluster node names", minimum=1, maximum=64),
            optional=True,
        ),
        server,
        comparison_examples,
        authentication,
        notifications,
        storage,
        replication,
        ports,
        services,
        backends,
    )

    return Configuration(
        "Application",
        "Application configuration",
        application,
        monitoring,
        Boolean("verbose", "Verbose logging", optional=True, default=False),
    )


if __name__ == "__main__":
    OUTPUT: Final[Path] = Path(__file__).parent
    CONFIG: Final[Configuration] = create_config()
    TEMPLATE: Final[Path] = CONFIG.template(OUTPUT, parents=True, overwrite=True)
