# ConfFlow

[![PyPI version](https://img.shields.io/pypi/v/confflow)](https://pypi.org/project/confflow/)
[![Python Versions](https://img.shields.io/pypi/pyversions/confflow)](https://pypi.org/project/confflow/)
[![Downloads](https://pepy.tech/badge/confflow)](https://pepy.tech/project/confflow)
[![Wheel](https://img.shields.io/pypi/wheel/confflow)](https://pypi.org/project/confflow/)

A Python library for **TOML** configuration management with built-in validation, cross-field rules, and type safety.

Define a `Configuration` and its tables, and ConfFlow will:

- Generate a fully commented `.toml` **template** for humans to fill in.
- **Load and validate** a `.toml` file against its declared entries and rules, raising descriptive errors on mismatch.
- Return the validated configuration as an **immutable**, read-only mapping (`Mapping`/`tuple`/`frozenset`).

## Table of Contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [Core concepts](#core-concepts)
  - [Configuration](#configuration)
  - [Members](#members)
  - [Definitions](#definitions)
  - [Rules](#rules)
- [Custom definitions](#custom-definitions)
- [Errors](#errors)
- [Full example](#full-example)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
pip install confflow
```

Requires Python 3.11+.

## Quick start

```python
from confflow import Configuration, Number, Text

configuration = Configuration(
    "Application",
    "Example application configuration.",
    Text("host", "Server hostname"),
    Number("port", "Server port", minimum=1, maximum=65535),
    Number("retries", "Maximum retry count", optional=True, default=3, minimum=0, maximum=10),
)

# Write a commented .toml template to a directory (application.toml).
configuration.template("./examples", overwrite=True)

# Load and validate an existing .toml file.
data = configuration.load("./examples/config.toml")
print(data["host"], data["port"])
```

`data` is a read-only `ConfigurationData` (`Mapping[str, ConfigurationValue]`) — nested tables
become nested mappings, arrays become tuples (or `frozenset`s when declared `unique=True`), and maps
become mappings keyed by their TOML table keys.

## Core concepts

### Configuration

`Configuration` is the top-level facade you interact with:

```python
Configuration(name, description, *members, rules=())
```

- `template(directory, *, overwrite=False)` — writes `<name.lower()>.toml` into `directory`, fully
  commented with each member's description, required/optional status, type, default, and any rules
  that reference it.
- `load(path)` — parses the `.toml` file, validates it against the configuration, and returns an immutable
  `ConfigurationData`.

`Configuration` composes the root entries and rules. Tables, arrays of tables, and maps of tables
own their nested entries and rules directly.

### Builder

`ConfigurationBuilder` provides fluent helpers for scalar TOML types. Add tables and custom entries
with `.add()`; there is intentionally no `.Table()` helper:

```python
from confflow import ConfigurationBuilder, Table

builder = ConfigurationBuilder(
  "Application",
  "Example configuration.",
)
configuration = (
  builder.Text("application_name", "Display name", optional=True)
  .add(
    Table("server", "Server settings.")
    .Text("password", "Server password", optional=True)
    .Text("token", "Server token", optional=True)
    .ExactlyOneOf("password", "token")
  )
  .build()
)
```

The scalar helpers are `.Text()`, `.Number()`, `.Decimal()`, `.Boolean()`, `.LocalDate()`,
`.LocalTime()`, `.LocalDateTime()`, and `.OffsetDateTime()`.

### Members

```python
from confflow import Configuration, Table, Text, Number, Boolean

server_fields = (
  Text("host", "Server hostname"),
  Number("port", "Server port"),
  Boolean("tls", "Whether TLS is enabled", optional=True, default=True),
)

configuration = Configuration("Application", "Example configuration.",
  Table("server", "Server connection settings.", entries=server_fields),
)
```

Entries are the named values and TOML tables composed by a `Configuration`, `Table`, table-shaped
`Array`, or table-valued `Mapping`:

| Member | Purpose |
| --- | --- |
| `Scalar` (for example `Text(name, ...)`) | A single scalar value backed by a `Definition`. |
| `Table(name, description="", *, optional=False, entries, rules=None)` | A TOML table with declared entries and optional sibling rules. |
| `Array(name, description, *, optional=False, element=Definition, ...)` | An array of scalar values. `unique=True` returns a `frozenset`. |
| `Array(name, description, *, optional=False, entries, rules=None, ...)` | An array of tables with declared entries and optional per-table rules. |
| `Mapping(name, description="", *, optional=False, value=Definition, ...)` | A dynamic-key TOML table with scalar values. |
| `Mapping(name, description="", *, optional=False, entries, rules=None, ...)` | A dynamic-key TOML table whose values are tables. |

### Definitions

Definitions describe and validate scalar TOML values (`Scalar` entries, scalar `Array` elements,
`Mapping` values/keys):

| Definition | TOML type | Notable options |
| --- | --- | --- |
| `Text` | string | `minimum_length`, `maximum_length`, `exact_length`, `pattern` |
| `Number` | integer | `minimum`, `maximum` (bounded to TOML's signed 64-bit range) |
| `Decimal` | float | `minimum`, `maximum` (rejects `NaN`) |
| `Boolean` | boolean | — |
| `LocalDate` | local date | `minimum`, `maximum` |
| `LocalTime` | local time | `minimum`, `maximum` |
| `LocalDateTime` | local date-time | `minimum`, `maximum` |
| `OffsetDateTime` | offset date-time | `minimum`, `maximum` |

Text, numeric, and date/time scalar types also have `*Literal` counterparts that restrict the value
to a fixed set via variadic values (at least two unique values of the same type):

```python
from confflow import TextLiteral

TextLiteral(
    "environment",
    "Deployment environment",
  "development",
  "staging",
  "production",
    default="development",
)
```

### Rules

Rules express relationships between sibling entries of a `Configuration`, `Table`, table-shaped
`Array`, or table-valued `Mapping`, and are checked when the configuration is loaded:

| Rule | Signature | Meaning |
| --- | --- | --- |
| `MutuallyExclusive` | `(*members)` | At most one of `members` may be present. |
| `ExactlyOneOf` | `(*members)` | Exactly one of `members` must be present. |
| `AtLeastOneOf` | `(*members)` | At least one of `members` must be present. |
| `AllOrNone` | `(*members)` | Either all of `members` are present, or none of them are. |
| `Requires` | `(source, target)` | If `source` is present, `target` must be present too. |
| `RequiresAny` | `(source, *targets)` | If `source` is present, at least one of `targets` must be present. |
| `RequiresAll` | `(source, *targets)` | If `source` is present, all of `targets` must be present. |
| `Forbids` | `(source, target)` | If `source` is present, `target` must not be present. |
| `ForbidsAny` | `(source, *targets)` | If `source` is present, none of `targets` may be present. |

```python
from confflow import ExactlyOneOf, Table, Text

password = Text("password", "Password used by this server", optional=True)
token = Text("token", "Token used by this server", optional=True)

Table(
  "server",
  "Server connection settings.",
  entries=(password, token),
    rules=(ExactlyOneOf(password, token),),
)
```

## Custom fields

Subclass a scalar field such as `Text` or `Number` and override `_validate()` for additional
domain-specific checks. The base field applies its declared definition first:

```python
from typing import cast, final
from confflow import InvalidValueError, Number, Text

@final
class Email(Text):
    __slots__ = ()

  def _validate(self, value: object) -> None:
    email: str = cast(str, value)
        local_part, separator, domain = email.partition("@")
        if separator == "" or local_part == "" or domain == "" or "@" in domain:
      raise InvalidValueError("expected an email address")


@final
class Port(Number):
  __slots__ = ()

  def _validate(self, value: object) -> None:
    port: int = cast(int, value)
    if port < 1 or port > 65535:
      raise InvalidValueError("port must be between 1 and 65535")
```

## Errors

| Exception | Raised when |
| --- | --- |
| `SchemaError` | A configuration, container, definition, or rule is constructed with invalid arguments (a programming error, caught early). |
| `InvalidValueError` | A loaded value fails a `Definition`'s `validate()` check. |
| `ValidationError` | A loaded configuration violates a `Rule`. |

## Full example

See [`examples/example.py`](examples/example.py) for an end-to-end configuration covering every
definition type, `Table`, `Array`, `Mapping`, custom fields, and every rule type. It generates
[`examples/application.toml`](examples/application.toml) as a template and validates
[`examples/config.toml`](examples/config.toml) against the declared configuration:

```bash
uv run python examples/example.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
