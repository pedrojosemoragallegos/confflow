from __future__ import annotations

from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import ClassVar, Final, cast, final

from confflow import (
    Configuration,
    ConfigurationBuilder,
    InvalidValueError,
    Number,
    Table,
    Text,
    TextLiteral,
)


@final
class Email(Text):
    __slots__ = ()

    def _validate(self, value: object) -> None:
        email: str = cast(typ="str", val=value)
        local_part, separator, domain = email.partition("@")
        if separator == "" or local_part == "" or domain == "" or "@" in domain:
            raise InvalidValueError("expected an email address")
        if "." not in domain:
            raise InvalidValueError("email domain must contain a dot")


@final
class Port(Number):
    __slots__ = ()

    _MAXIMUM_PORT_NUMBER: ClassVar[int] = 65535

    def _validate(self, value: object) -> None:
        port: int = cast(typ="int", val=value)
        if port < 1 or port > self._MAXIMUM_PORT_NUMBER:
            raise InvalidValueError(
                f"port must be between 1 and {self._MAXIMUM_PORT_NUMBER}"
            )


if __name__ == "__main__":
    primary: Final[Table] = (
        Table("primary", "Primary server")
        .Text("host", "Server hostname", minimum=1)
        .add(Port("port", "Server port"))
        .Boolean("tls", "Whether TLS is enabled", optional=True, default=True)
        .Text("password", "Password used by this server", optional=True)
        .Text("token", "Token used by this server", optional=True)
        .ExactlyOneOf("password", "token")
    )

    account: Final[Table] = (
        Table("account", "Account settings", optional=True)
        .add(
            Email(
                "email",
                "Account email address\nUsed for account notifications",
                default="admin@example.com",
                minimum=5,
            )
        )
        .Text(
            "username",
            "Account username",
            minimum=3,
            maximum=32,
            pattern=r"[a-z][a-z0-9_]*",
        )
        .Text(
            "country_code",
            "Two-letter country code",
            optional=True,
            length=2,
            pattern=r"[A-Z]{2}",
        )
    )

    lifecycle: Final[Table] = (
        Table("lifecycle", "Lifecycle settings", optional=True)
        .OffsetDateTime(
            "created_at",
            "Configuration creation instant",
            minimum=datetime(year=2026, month=1, day=1, tzinfo=UTC),
            maximum=datetime(year=2027, month=1, day=1, tzinfo=UTC),
        )
        .LocalDateTime(
            "maintenance_at",
            "Local maintenance date and time",
            optional=True,
            minimum=datetime(year=2026, month=1, day=1, hour=0, minute=0),
            maximum=datetime(year=2027, month=1, day=1, hour=0, minute=0),
        )
        .LocalDate(
            "launch_date",
            "Application launch date",
            optional=True,
            minimum=date(year=2026, month=1, day=1),
            maximum=date(year=2027, month=1, day=1),
        )
        .LocalTime(
            "daily_time",
            "Daily execution time",
            optional=True,
            minimum=time(hour=0, minute=0),
            maximum=time(hour=23, minute=59, second=59),
        )
    )

    deployment: Final[Table] = (
        Table("deployment", "Deployment settings", optional=True)
        .TextLiteral(
            "environment",
            "Deployment environment",
            "development",
            "staging",
            "production",
            optional=True,
            default="development",
        )
        .NumberLiteral(
            "workers",
            "Worker count preset",
            1,
            2,
            4,
            8,
            optional=True,
            default=4,
        )
        .DecimalLiteral(
            "ratio",
            "Ratio preset",
            0.5,
            1.0,
            2.0,
            optional=True,
            default=1.0,
        )
        .OffsetDateTimeLiteral(
            "release_instant",
            "Allowed release instants",
            datetime(year=2026, month=10, day=1, hour=12, minute=0, tzinfo=UTC),
            datetime(year=2026, month=11, day=1, hour=12, minute=0, tzinfo=UTC),
            optional=True,
        )
        .LocalDateTimeLiteral(
            "local_release",
            "Allowed local release date-times",
            datetime(year=2026, month=10, day=1, hour=12, minute=0),
            datetime(year=2026, month=11, day=1, hour=12, minute=0),
            optional=True,
        )
        .LocalDateLiteral(
            "billing_day",
            "Allowed billing dates",
            date(year=2026, month=10, day=1),
            date(year=2026, month=11, day=1),
            optional=True,
        )
        .LocalTimeLiteral(
            "backup_time",
            "Allowed backup times",
            time(hour=1, minute=0),
            time(hour=2, minute=0),
            optional=True,
        )
    )

    server_settings: Final[Table] = (
        Table("server_settings", "Server settings", optional=True)
        .add(primary)
        .Array(
            "servers",
            "Additional servers",
            optional=True,
            entries=primary.entries,
            rules=primary.rules,
            minimum_length=1,
            maximum_length=3,
        )
        .Mapping(
            "named_servers",
            "Named server configurations",
            optional=True,
            entries=primary.entries,
            rules=primary.rules,
            minimum_entries=1,
            maximum_entries=3,
        )
    )

    notifications: Final[Table] = (
        Table("notifications", "Notification settings", optional=True)
        .Array(
            "notification_emails",
            "Notification email addresses",
            optional=True,
            element=Email("notification_email", "One notification email"),
            minimum_length=1,
            maximum_length=5,
            unique=True,
        )
        .Mapping(
            "contacts_by_role",
            "Named contact email addresses",
            optional=True,
            value=Email("contact_email", "Contact email address"),
        )
    )

    metadata: Final[Table] = (
        Table("metadata", "Metadata settings", optional=True)
        .Array(
            "roles",
            "Assigned roles",
            optional=True,
            element=TextLiteral("role", "One role", "admin", "operator", "viewer"),
            unique=True,
        )
        .Mapping(
            "labels",
            "Free-form labels",
            optional=True,
            key=Text("label_name", "Label name", pattern=r"[a-z][a-z0-9_]*"),
            value=Text("label_value", "Label value", minimum=1),
            minimum_entries=1,
            maximum_entries=5,
        )
    )

    runtime: Final[Table] = (
        Table("runtime", "Runtime settings", optional=True)
        .Number(
            "retries",
            "Maximum retry count",
            optional=True,
            default=3,
            minimum=0,
            maximum=10,
        )
        .Decimal(
            "timeout",
            "Request timeout in seconds",
            optional=True,
            default=5.0,
            minimum=0.0,
            maximum=60.0,
        )
        .Boolean("debug", "Enable debug mode", optional=True, default=False)
    )

    configuration_builder: Final[ConfigurationBuilder] = ConfigurationBuilder(
        "Application",
        "Comprehensive TOML configuration example.\n"
        "Demonstrates every supported TOML-facing feature.",
    )
    configuration_builder.Text(
        "application_name", "Application display name", optional=True
    )

    configuration_builder.Text(
        "mutually_exclusive_left", "First mutually exclusive option", optional=True
    )
    configuration_builder.Text(
        "mutually_exclusive_right", "Second mutually exclusive option", optional=True
    )
    configuration_builder.MutuallyExclusive(
        "mutually_exclusive_left", "mutually_exclusive_right"
    )

    configuration_builder.Text(
        "exactly_one_left", "First exactly-one option", optional=True
    )
    configuration_builder.Text(
        "exactly_one_right", "Second exactly-one option", optional=True
    )
    configuration_builder.ExactlyOneOf("exactly_one_left", "exactly_one_right")

    configuration_builder.Text(
        "at_least_one_left", "First at-least-one option", optional=True
    )
    configuration_builder.Text(
        "at_least_one_right", "Second at-least-one option", optional=True
    )
    configuration_builder.AtLeastOneOf("at_least_one_left", "at_least_one_right")

    configuration_builder.Text(
        "all_or_none_left", "First all-or-none option", optional=True
    )
    configuration_builder.Text(
        "all_or_none_right", "Second all-or-none option", optional=True
    )
    configuration_builder.AllOrNone("all_or_none_left", "all_or_none_right")

    configuration_builder.Text(
        "requires_source", "Source of a requires rule", optional=True
    )

    configuration_builder.Text("requires_target", "Required target", optional=True)

    configuration_builder.Requires(source="requires_source", target="requires_target")

    configuration_builder.Text(
        "requires_any_source", "Source of a requires-any rule", optional=True
    )

    configuration_builder.Text(
        "requires_any_left", "First requires-any target", optional=True
    )

    configuration_builder.Text(
        "requires_any_right", "Second requires-any target", optional=True
    )

    configuration_builder.RequiresAny(
        "requires_any_left", "requires_any_right", source="requires_any_source"
    )

    configuration_builder.Text(
        "requires_all_source", "Source of a requires-all rule", optional=True
    )

    configuration_builder.Text(
        "requires_all_left", "First requires-all target", optional=True
    )

    configuration_builder.Text(
        "requires_all_right", "Second requires-all target", optional=True
    )

    configuration_builder.RequiresAll(
        "requires_all_left", "requires_all_right", source="requires_all_source"
    )

    configuration_builder.Text(
        "forbids_source", "Source of a forbids rule", optional=True
    )

    configuration_builder.Text("forbids_target", "Forbidden target", optional=True)

    configuration_builder.Forbids(source="forbids_source", target="forbids_target")

    configuration_builder.Text(
        "forbids_any_source", "Source of a forbids-any rule", optional=True
    )

    configuration_builder.Text(
        "forbids_any_left", "First forbids-any target", optional=True
    )

    configuration_builder.Text(
        "forbids_any_right", "Second forbids-any target", optional=True
    )

    configuration_builder.ForbidsAny(
        "forbids_any_left",
        "forbids_any_right",
        source="forbids_any_source",
    )

    configuration_builder.add(account)

    configuration_builder.add(lifecycle)

    configuration_builder.add(deployment)

    configuration_builder.add(server_settings)

    configuration_builder.add(notifications)

    configuration_builder.add(metadata)

    configuration_builder.add(runtime)

    configuration: Final[Configuration] = configuration_builder.build()

    directory: Final[Path] = Path(__file__).parent

    configuration.template(directory, overwrite=True)
