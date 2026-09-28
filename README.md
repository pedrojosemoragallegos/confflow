# ConfFlow

[![PyPI version](https://img.shields.io/pypi/v/confflow)](https://pypi.org/project/confflow/)
[![Python Versions](https://img.shields.io/pypi/pyversions/confflow)](https://pypi.org/project/confflow/)
[![Downloads](https://pepy.tech/badge/confflow)](https://pepy.tech/project/confflow)
[![Wheel](https://img.shields.io/pypi/wheel/confflow)](https://pypi.org/project/confflow/)

A Python library for schema-based **TOML** configuration management with built-in validation, cross-field rules, and type safety.

Define a `Schema` once, and ConfFlow will:

- Generate a fully commented `.toml` **template** for humans to fill in.
- **Load and validate** a `.toml` file against that schema, raising descriptive errors on mismatch.
- Return the validated configuration as an **immutable**, read-only mapping (`Mapping`/`tuple`/`frozenset`).

## Table of Contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [Core concepts](#core-concepts)
  - [Configuration](#configuration)
  - [Schema](#schema)
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
    Text("host", "Server hostname", required=True),
    Number("port", "Server port", required=True, minimum=1, maximum=65535),
    Number("retries", "Maximum retry count", default=3, minimum=0, maximum=10),
)

# Write a commented .toml template to a directory (application.toml).
configuration.template("./examples", overwrite=True)

# Load and validate an existing .toml file.
data = configuration.load("./examples/config.toml")
print(data["host"], data["port"])
```

`data` is a read-only `ConfigurationData` (`Mapping[str, ConfigurationValue]`) — nested sections
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
- `load(path)` — parses the `.toml` file, validates it against the schema, and returns an immutable
  `ConfigurationData`.

### Schema

A `Schema` bundles members and rules and is used both as the root of a `Configuration` and to define
reusable nested sections:

```python
from confflow import Schema, Text, Number, Boolean

server_schema = Schema(
    "Server",
    "Reusable server connection settings.",
    Text("host", "Server hostname", required=True),
    Number("port", "Server port", required=True),
    Boolean("tls", "Whether TLS is enabled", default=True),
)
```

Schemas validate themselves at construction time: member names must be unique, rule targets must be
direct members of the same schema, and no rule may create a direct contradiction (e.g. `Requires` and
`Forbids` on the same source/target pair).

### Members

Members are the entries that make up a `Schema`, each a subclass of `Entry`:

| Member | Purpose |
| --- | --- |
| `Field(name, description, required, definition, default=None)` | A single scalar value backed by a `Definition`. |
| `Section(name, description="", *, required=False, schema)` | A nested table backed by another `Schema`. |
| `Array(name, description, element, *, required=False, minimum_length=None, maximum_length=None, unique=False)` | A list whose `element` is a `Definition` (scalar array) or `Schema` (array of tables). `unique=True` returns a `frozenset` and requires a scalar element. |
| `Map(name, description="", *, required=False, value, key=None, minimum_entries=None, maximum_entries=None)` | A free-form TOML table keyed by string, with `value` as a `Definition` or `Schema` and an optional `key` `Definition[str]` validator. |

### Definitions

Definitions describe and validate scalar TOML values (`Field`, `Array` elements, `Map` values/keys):

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

Each scalar type also has a `*Literal` counterpart (`TextLiteral`, `NumberLiteral`, `DecimalLiteral`,
`BooleanLiteral`, `LocalDateLiteral`, `LocalTimeLiteral`, `LocalDateTimeLiteral`,
`OffsetDateTimeLiteral`) that restricts the value to a fixed set via `values=(...)` (at least two
unique, same-typed values):

```python
from confflow import TextLiteral

TextLiteral(
    "environment",
    "Deployment environment",
    values=("development", "staging", "production"),
    default="development",
)
```

### Rules

Rules express relationships between sibling members of the same `Schema` and are checked when the
configuration is loaded:

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
from confflow import ExactlyOneOf, Schema, Text

password = Text("password", "Password used by this server")
token = Text("token", "Token used by this server")

Schema(
    "Server",
    "Reusable server connection settings.",
    password,
    token,
    rules=(ExactlyOneOf(password, token),),
)
```

## Custom definitions

Subclass an existing `Definition` (or `Scalar`) to add domain-specific validation, calling
`super().validate(...)` first:

```python
from typing import cast, final, override
from confflow import InvalidValueError, Text

@final
class Email(Text):
    __slots__ = ()

    @override
    def validate(self, value: object, path: tuple[str | int, ...]) -> None:
        super().validate(value, path)
        email = cast(str, value)
        local_part, separator, domain = email.partition("@")
        if separator == "" or local_part == "" or domain == "" or "@" in domain:
            raise InvalidValueError("expected an email address", path)
```

## Errors

| Exception | Raised when |
| --- | --- |
| `SchemaError` | A `Schema`, `Definition`, or member/rule is constructed with invalid arguments (a programming error, caught early). |
| `InvalidValueError` | A loaded value fails a `Definition`'s `validate()` check. |
| `ValidationError` | A loaded configuration violates a `Rule`. |

## Full example

See [`examples/example.py`](examples/example.py) for an end-to-end configuration covering every
definition type, `Section`, `Array`, `Map`, custom definitions, and every rule type. It generates
[`examples/application.toml`](examples/application.toml) as a template and validates
[`examples/config.toml`](examples/config.toml) against the schema:

```bash
uv run python examples/example.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
