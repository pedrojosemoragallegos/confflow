from __future__ import annotations

from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast, final

from typing_extensions import override

from confflow import (
    AllOrNone,
    Array,
    AtLeastOneOf,
    Boolean,
    BooleanLiteral,
    Configuration,
    ConfigurationData,
    Decimal,
    DecimalLiteral,
    ExactlyOneOf,
    Forbids,
    ForbidsAny,
    InvalidValueError,
    LocalDate,
    LocalDateLiteral,
    LocalDateTime,
    LocalDateTimeLiteral,
    LocalTime,
    LocalTimeLiteral,
    Map,
    MutuallyExclusive,
    Number,
    NumberLiteral,
    OffsetDateTime,
    OffsetDateTimeLiteral,
    Requires,
    RequiresAll,
    RequiresAny,
    Schema,
    Section,
    Text,
    TextLiteral,
)

if TYPE_CHECKING:
    from confflow.core.rules import Rule


@final
class Email(Text):
    __slots__ = ()

    @override
    def validate(self, value: object, path: tuple[str | int, ...]) -> None:
        super().validate(value, path)
        email: str = cast(typ="str", val=value)
        local_part, separator, domain = email.partition("@")
        if separator == "" or local_part == "" or domain == "" or "@" in domain:
            raise InvalidValueError("expected an email address", path)
        if "." not in domain:
            raise InvalidValueError("email domain must contain a dot", path)


_MAXIMUM_PORT_NUMBER: Final = 65535


@final
class Port(Number):
    __slots__ = ()

    @override
    def validate(self, value: object, path: tuple[str | int, ...]) -> None:
        super().validate(value, path)
        port: int = cast(typ="int", val=value)
        if port < 1 or port > _MAXIMUM_PORT_NUMBER:
            raise InvalidValueError("port must be between 1 and 65535", path)


if __name__ == "__main__":
    server_host: Final[Text] = Text(
        "host",
        "Server hostname",
        required=True,
        minimum_length=1,
    )

    server_port: Final[Port] = Port("port", "Server port", required=True)

    server_tls: Final[Boolean] = Boolean("tls", "Whether TLS is enabled", default=True)

    server_password: Final[Text] = Text("password", "Password used by this server")

    server_token: Final[Text] = Text("token", "Token used by this server")

    server_authentication_rule: Final[ExactlyOneOf] = ExactlyOneOf(
        server_password,
        server_token,
    )

    server_rules: tuple[Rule, ...] = (server_authentication_rule,)

    server_fields: Final = (
        server_host,
        server_port,
        server_tls,
        server_password,
        server_token,
    )

    server_schema: Final[Schema] = Schema(
        "Server",
        "Reusable server connection settings.",
        *server_fields,
        rules=server_rules,
    )

    primary: Final[Section] = Section(
        "primary",
        "Primary server",
        required=True,
        schema=server_schema,
    )

    servers: Final[Array] = Array(
        "servers",
        "Additional servers",
        server_schema,  # TODO: keyword and positional only
        minimum_length=1,
        maximum_length=3,
    )

    named_servers: Final[Map] = Map(
        "named_servers",
        "Named server configurations",
        value=server_schema,
        minimum_entries=1,
        maximum_entries=3,
    )

    mutually_exclusive_left: Final[Text] = Text(
        "mutually_exclusive_left",
        "First mutually exclusive option",
    )

    mutually_exclusive_right: Final[Text] = Text(
        "mutually_exclusive_right",
        "Second mutually exclusive option",
    )

    exactly_one_left: Final[Text] = Text("exactly_one_left", "First exactly-one option")

    exactly_one_right: Final[Text] = Text(
        "exactly_one_right", "Second exactly-one option"
    )

    at_least_one_left: Final[Text] = Text(
        "at_least_one_left", "First at-least-one option"
    )

    at_least_one_right: Final[Text] = Text(
        "at_least_one_right", "Second at-least-one option"
    )

    all_or_none_left: Final[Text] = Text("all_or_none_left", "First all-or-none option")

    all_or_none_right: Final[Text] = Text(
        "all_or_none_right", "Second all-or-none option"
    )

    requires_source: Final[Text] = Text("requires_source", "Source of a requires rule")

    requires_target: Final[Text] = Text("requires_target", "Required target")

    requires_any_source: Final[Text] = Text(
        "requires_any_source", "Source of a requires-any rule"
    )

    requires_any_left: Final[Text] = Text(
        "requires_any_left", "First requires-any target"
    )

    requires_any_right: Final[Text] = Text(
        "requires_any_right", "Second requires-any target"
    )

    requires_all_source: Final[Text] = Text(
        "requires_all_source", "Source of a requires-all rule"
    )

    requires_all_left: Final[Text] = Text(
        "requires_all_left", "First requires-all target"
    )

    requires_all_right: Final[Text] = Text(
        "requires_all_right", "Second requires-all target"
    )

    forbids_source: Final[Text] = Text("forbids_source", "Source of a forbids rule")

    forbids_target: Final[Text] = Text("forbids_target", "Forbidden target")

    forbids_any_source: Final[Text] = Text(
        "forbids_any_source", "Source of a forbids-any rule"
    )

    forbids_any_left: Final[Text] = Text("forbids_any_left", "First forbids-any target")

    forbids_any_right: Final[Text] = Text(
        "forbids_any_right", "Second forbids-any target"
    )

    mutually_exclusive_rule: Final[MutuallyExclusive] = MutuallyExclusive(
        mutually_exclusive_left,
        mutually_exclusive_right,
    )

    exactly_one_rule: Final[ExactlyOneOf] = ExactlyOneOf(
        exactly_one_left,
        exactly_one_right,
    )

    at_least_one_rule: Final[AtLeastOneOf] = AtLeastOneOf(
        at_least_one_left,
        at_least_one_right,
    )

    all_or_none_rule: Final[AllOrNone] = AllOrNone(
        all_or_none_left,
        all_or_none_right,
    )

    requires_rule: Final[Requires] = Requires(  # TODO: keyword only?
        requires_source,
        requires_target,
    )
    requires_any_rule: Final[RequiresAny] = RequiresAny(
        requires_any_source,
        requires_any_left,
        requires_any_right,
    )
    requires_all_rule: Final[RequiresAll] = RequiresAll(
        requires_all_source,
        requires_all_left,
        requires_all_right,
    )

    forbids_rule: Final[Forbids] = Forbids(  # TODO: keyword only?
        forbids_source,
        forbids_target,
    )

    forbids_any_rule: Final[ForbidsAny] = ForbidsAny(
        forbids_any_source,
        forbids_any_left,
        forbids_any_right,
    )

    rules: tuple[Rule, ...] = (
        mutually_exclusive_rule,
        exactly_one_rule,
        at_least_one_rule,
        all_or_none_rule,
        requires_rule,
        requires_any_rule,
        requires_all_rule,
        forbids_rule,
        forbids_any_rule,
    )

    account: Final[Section] = Section(
        "account",
        "Account settings",
        schema=Schema(
            "Account",
            "Account identity settings.",
            Email(
                "email",
                "Account email address\nUsed for account notifications",
                required=True,
                default="admin@example.com",
                minimum_length=5,
            ),
            Text(
                "username",
                "Account username",
                required=True,
                minimum_length=3,
                maximum_length=32,
                pattern=r"[a-z][a-z0-9_]*",
            ),
            Text(
                "country_code",
                "Two-letter country code",
                exact_length=2,
                pattern=r"[A-Z]{2}",
            ),
        ),
    )

    runtime: Final[Section] = Section(
        "runtime",
        "Runtime settings",
        schema=Schema(
            "Runtime",
            "Runtime behavior settings.",
            Number(
                "retries",
                "Maximum retry count",
                default=3,
                minimum=0,
                maximum=10,
            ),
            Decimal(
                "timeout",
                "Request timeout in seconds",
                default=5.0,
                minimum=0.0,
                maximum=60.0,
            ),
            Boolean("debug", "Enable debug mode", default=False),
        ),
    )

    lifecycle: Final[Section] = Section(
        "lifecycle",
        "Lifecycle settings",
        schema=Schema(
            "Lifecycle",
            "Application lifecycle and scheduling settings.",
            OffsetDateTime(
                "created_at",
                "Configuration creation instant",
                required=True,
                minimum=datetime(year=2026, month=1, day=1, tzinfo=UTC),
                maximum=datetime(year=2027, month=1, day=1, tzinfo=UTC),
            ),
            LocalDateTime(
                "maintenance_at",
                "Local maintenance date and time",
                minimum=datetime(year=2026, month=1, day=1, hour=0, minute=0),
                maximum=datetime(year=2027, month=1, day=1, hour=0, minute=0),
            ),
            LocalDate(
                "launch_date",
                "Application launch date",
                minimum=date(year=2026, month=1, day=1),
                maximum=date(year=2027, month=1, day=1),
            ),
            LocalTime(
                "daily_time",
                "Daily execution time",
                minimum=time(hour=0, minute=0),
                maximum=time(hour=23, minute=59, second=59),
            ),
        ),
    )

    deployment: Final[Section] = Section(
        "deployment",
        "Deployment settings",
        schema=Schema(
            "Deployment",
            "Deployment and release settings.",
            TextLiteral(
                "environment",
                "Deployment environment",
                values=("development", "staging", "production"),  # TODO: *values?
                default="development",
            ),
            NumberLiteral(
                "workers",
                "Worker count preset",
                values=(1, 2, 4, 8),  # TODO: *values?
                default=4,
            ),
            DecimalLiteral(
                "ratio",
                "Ratio preset",
                values=(0.5, 1.0, 2.0),  # TODO: *values?
                default=1.0,
            ),
            (
                BooleanLiteral(  # TODO: booleanliteral?? does it make any sense??
                    "feature_switch",
                    "Allowed feature-switch values",
                    values=(True, False),  # TODO: *values?
                    default=True,
                )
            ),
            OffsetDateTimeLiteral(
                "release_instant",
                "Allowed release instants",
                values=(  # TODO: *values?
                    datetime(year=2026, month=10, day=1, hour=12, minute=0, tzinfo=UTC),
                    datetime(year=2026, month=11, day=1, hour=12, minute=0, tzinfo=UTC),
                ),
            ),
            LocalDateTimeLiteral(
                "local_release",
                "Allowed local release date-times",
                values=(  # TODO: *values?
                    datetime(year=2026, month=10, day=1, hour=12, minute=0),
                    datetime(year=2026, month=11, day=1, hour=12, minute=0),
                ),
            ),
            LocalDateLiteral(
                "billing_day",
                "Allowed billing dates",
                values=(  # TODO: *values?
                    date(year=2026, month=10, day=1),
                    date(year=2026, month=11, day=1),
                ),
            ),
            LocalTimeLiteral(
                "backup_time",
                "Allowed backup times",
                values=(  # TODO: *values?
                    time(hour=1, minute=0),
                    time(hour=2, minute=0),
                ),
            ),
        ),
    )

    server_settings: Final[Section] = Section(
        "server_settings",
        "Server settings",
        schema=Schema(
            "Servers",
            "Server configuration settings.",
            primary,
            servers,
            named_servers,
        ),
    )

    notifications: Final[Section] = Section(
        "notifications",
        "Notification settings",
        schema=Schema(
            "Notifications",
            "Notification and contact settings.",
            Array(
                "notification_emails",
                "Notification email addresses",
                Email(
                    "notification_email",
                    "One notification email",
                ),
                minimum_length=1,
                maximum_length=5,
                unique=True,
            ),
            Map(
                "contacts_by_role",
                "Named contact email addresses",
                value=Email("contact_email", "Contact email address"),
            ),
        ),
    )

    metadata: Final[Section] = Section(
        "metadata",
        "Metadata settings",
        schema=Schema(
            "Metadata",
            "Role and label settings.",
            Array(
                "roles",
                "Assigned roles",
                TextLiteral(
                    "role",
                    "One role",
                    values=("admin", "operator", "viewer"),  # TODO: *values?
                ),
                unique=True,
            ),
            Map(
                "labels",
                "Free-form labels",
                key=Text(
                    "label_name",
                    "Label name",
                    pattern=r"[a-z][a-z0-9_]*",
                ),
                value=Text(
                    "label_value",
                    "Label value",
                    minimum_length=1,
                ),
                minimum_entries=1,
                maximum_entries=5,
            ),
        ),
    )

    section_fields: Final = (
        account,
        runtime,
        lifecycle,
        deployment,
        server_settings,
        notifications,
        metadata,
    )

    rule_fields: Final = (
        mutually_exclusive_left,
        mutually_exclusive_right,
        exactly_one_left,
        exactly_one_right,
        at_least_one_left,
        at_least_one_right,
        all_or_none_left,
        all_or_none_right,
        requires_source,
        requires_target,
        requires_any_source,
        requires_any_left,
        requires_any_right,
        requires_all_source,
        requires_all_left,
        requires_all_right,
        forbids_source,
        forbids_target,
        forbids_any_source,
        forbids_any_left,
        forbids_any_right,
    )

    fields: Final = (
        *section_fields,
        *rule_fields,
    )

    configuration: Final[Configuration] = Configuration(
        "Application",
        "Comprehensive TOML configuration example.\n"
        "Demonstrates every supported TOML-facing feature.",
        # TODO: create lists which you open here like *list_as_varibale_of_fields
        *fields,
        rules=rules,
    )

    directory: Final[Path] = Path(__file__).parent
    configuration.template(directory, overwrite=True)
    config: Final[Path] = directory / "config.toml"
    loaded: Final[ConfigurationData] = configuration.load(config)
