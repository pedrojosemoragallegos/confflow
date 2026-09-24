# ConfFlow

[![PyPI version](https://img.shields.io/pypi/v/confflow)](https://pypi.org/project/confflow/)
[![Python Versions](https://img.shields.io/pypi/pyversions/confflow)](https://pypi.org/project/confflow/)
[![Downloads](https://pepy.tech/badge/confflow)](https://pepy.tech/project/confflow)
[![Wheel](https://img.shields.io/pypi/wheel/confflow)](https://pypi.org/project/confflow/)

A Python library for schema-based **TOML** configuration management with built-in validation, constraints, and type safety.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [1. Define a schema](#1-define-a-schema)
  - [2. Generate a template](#2-generate-a-template)
  - [3. Load and validate](#3-load-and-validate)
- [Building Schemas](#building-schemas)
  - [Nested tables](#nested-tables)
  - [Arrays](#arrays)
  - [Arrays of tables](#arrays-of-tables)
  - [Fixed value sets](#fixed-value-sets)
  - [Adding independently-built fields](#adding-independently-built-fields)
  - [Custom field types](#custom-field-types)
- [Constraints](#constraints)
  - [Presence constraints](#presence-constraints)
  - [`Requires`](#requires)
  - [Comparison constraints](#comparison-constraints)
  - [Error handling](#error-handling)
- [API Reference](#api-reference)
  - [`Schema`](#schema)
  - [Field types](#field-types)
  - [`ConfigurationError`](#configurationerror)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Type-safe TOML fields**: `String`, `Integer`, `Float`, `Boolean`, `Literal`, `Date`, `Time`, `LocalDateTime`, `OffsetDateTime`, `Array`, `ArrayOfTables`
- **Nested schemas**: build hierarchical TOML tables with unlimited nesting depth
- **Field-level validation**: length/pattern constraints on strings, min/max on numbers, fixed value sets via `Literal`, length and element validation on arrays
- **Cross-field constraints**: `Exclusive`, `ExactlyOne`, `AtLeastOne`, `AllOrNone`, `Requires`, `Equal`, `NotEqual`, `LessThan`, `LessThanOrEqual`, `GreaterThan`, `GreaterThanOrEqual`
- **Template generation**: `schema.template(path)` writes a fully commented `.toml` file documenting every field, default, and constraint
- **Load & validate**: `schema.load(path)` reads and validates a TOML file; `schema.validate(data)` validates an already-parsed mapping
- **Fully typed**: ships a `py.typed` marker, all public APIs are annotated

## Installation

```bash
pip install confflow
```

## Quick Start

### 1. Define a schema

```python
from confflow import Schema, String, Integer, Boolean

app = Schema("app", "Application configuration")
app.String("name", "Application name", default="MyApp")
app.Integer("workers", "Worker count", default=4, minimum=1, maximum=32)

database = app.Schema("database", "Database settings")
database.String("host", "Database host", default="localhost")
database.Integer("port", "Database port", default=5432, minimum=1, maximum=65535)
database.Boolean("ssl", "Use SSL", default=True)
```

`Schema.Schema(...)` registers a nested table on the parent and returns the **child** schema, so keep a reference (`database` above) to keep building it.

### 2. Generate a template

```python
app.template("app.toml")
```

```toml
# Application configuration

# Application name
# string | optional | default='MyApp'
name = "MyApp"

# Worker count
# integer | optional | default=4 | minimum=1 | maximum=32
workers = 4

# Database settings
[database]
# Database host
# string | optional | default='localhost'
host = "localhost"

# Database port
# integer | optional | default=5432 | minimum=1 | maximum=65535
port = 5432

# Use SSL
# boolean | optional | default=true
ssl = true
```

### 3. Load and validate

```python
config = app.load("app.toml")
print(config["database"]["host"])  # "localhost"

# Or validate an already-parsed mapping directly
config = app.validate({"name": "X", "database": {"host": "h", "port": 1}})
```

Both `load()` and `validate()` return a plain `dict[str, TOMLValue]` and raise `ConfigurationError` (a `ValueError` subclass with a `.path` property) on failure.

## Building Schemas

### Nested tables

Use `schema.Schema(name, description)` to create a nested TOML table. It registers the child on the parent and returns the child, so keep a reference to keep building it:

```python
root = Schema("app", "Application configuration")
cache = root.Schema("cache", "Cache settings")
cache.String("backend", "Cache backend", default="redis")
cache.Integer("ttl", "TTL in seconds", default=3600)
```

### Arrays

`Array` validates a list whose elements are each validated against a nested `Field`:

```python
from confflow import Array, String

root.Array(
    "tags",
    "Tags",
    element=String("item", "A tag"),
    default=["a", "b"],
    min_length=1,
    max_length=10,
)
```

### Arrays of tables

`ArrayOfTables` validates a list of TOML tables, each checked against its own `Schema`:

```python
user = Schema("user", "A user")
user.String("name", "User name")
user.Boolean("admin", "Admin flag", default=False)

root.ArrayOfTables("users", "Users", user, default=[{"name": "bob"}])
```

### Fixed value sets

`Literal` restricts a field to a fixed set of scalar values (an enum):

```python
from confflow import Literal

root.Literal("env", "Deployment environment", "dev", "staging", "prod", default="dev")
```

### Adding independently-built fields

Every `schema.<Type>(...)` method (e.g. `schema.String(...)`) is sugar for constructing the field and calling `schema.add(field)`. Construct a field directly when you need to keep a reference to it — for example, to use it in a cross-field constraint:

```python
from confflow import String

api_key = String("api_key", "API key", default=None)
api_secret = String("api_secret", "API secret", default=None)
root.add(api_key, api_secret)
```

### Custom field types

For simple patterns, use `String`'s built-in `pattern` support rather than subclassing:

```python
from confflow import String

EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

root.add(String("contact", "Contact email", required=True, pattern=EMAIL_PATTERN))
```

`_typecheck` exists only to check a value's Python type, so it shouldn't hold business rules. To add validation to an existing field, override `validate` instead — call `super().validate()` first, then apply extra checks:

```python
import re

from typing_extensions import override
from confflow import ConfigurationError, String

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

class Email(String):
    @override
    def validate(self, value: object, path: str, /) -> str:
        value = super().validate(value, path)
        if EMAIL_PATTERN.fullmatch(value) is None:
            raise ConfigurationError(path, "invalid Email value")
        return value

root.add(Email("contact", "Contact email", required=True))
```

To introduce an entirely new base type (not built on an existing field), subclass `Field` directly and implement `_typecheck` for the type check.

## Constraints

Constraints are added via methods on `Schema` and are checked after every field in that schema has validated.

### Presence constraints

Take any number of fields/nested schemas and check how many of them are present in the input:

```python
root.Exclusive(aws_region, gcp_project)   # at most one may be set
root.ExactlyOne(aws_region, gcp_project)  # exactly one must be set
root.AtLeastOne(aws_region, gcp_project)  # at least one must be set
root.AllOrNone(aws_region, gcp_project)   # either all are set, or none are
```

### `Requires`

```python
root.Requires(api_secret, api_key)  # if api_secret is set, api_key must be too
```

### Comparison constraints

Compare two fields of the **same field type**. The ordering comparisons (`LessThan`, `LessThanOrEqual`, `GreaterThan`, `GreaterThanOrEqual`) additionally require an orderable field type (`String`, `Integer`, `Float`, `Date`, `Time`, `LocalDateTime`, `OffsetDateTime`):

```python
root.Equal(a, b)
root.NotEqual(a, b)
root.LessThan(min_value, max_value)
root.LessThanOrEqual(min_value, max_value)
root.GreaterThan(a, b)
root.GreaterThanOrEqual(a, b)
```

Constraints are also rendered in generated templates as labeled, commented blocks:

```toml
# ───────────────────────────── EXCLUSIVE ─────────────────────────────
# At most one field in this group may be set.

# AWS region
# string | optional
aws_region =

# GCP project
# string | optional
gcp_project =

# ─────────────────────────── END EXCLUSIVE ───────────────────────────
```

### Error handling

Validation failures raise `ConfigurationError`, a `ValueError` subclass exposing the failing `path`:

```python
from confflow import ConfigurationError

try:
    root.validate({"api_secret": "x"})  # api_key is missing
except ConfigurationError as exc:
    print(exc.path)  # "app"
    print(exc)        # "app: Requires(api_secret, api_key)"
```

## API Reference

### `Schema`

**`Schema(name: str, description: str)`** creates a schema representing a TOML table.

Field-builder methods construct the field and call `add()`, returning `self` for chaining (except `Schema(...)` itself, which returns the new **nested** schema):

- `schema.String(name, description, *, required=False, default=None, min_length=None, max_length=None, pattern=None)`
- `schema.Literal(name, description, *values, required=False, default=None)`
- `schema.Integer(name, description, *, required=False, default=None, minimum=None, maximum=None)`
- `schema.Float(name, description, *, required=False, default=None, minimum=None, maximum=None)`
- `schema.Boolean(name, description, *, required=False, default=None)`
- `schema.Date(name, description, *, required=False, default=None)`
- `schema.Time(name, description, *, required=False, default=None)`
- `schema.LocalDateTime(name, description, *, required=False, default=None)`
- `schema.OffsetDateTime(name, description, *, required=False, default=None)`
- `schema.Array(name, description, *, element, required=False, default=None, min_length=None, max_length=None)`
- `schema.ArrayOfTables(name, description, schema, *, required=False, default=None)`
- `schema.Schema(name, description)` — creates and returns a nested `Schema`

Constraint-builder methods:

- `schema.Exclusive(*targets)`, `schema.ExactlyOne(*targets)`, `schema.AtLeastOne(*targets)`, `schema.AllOrNone(*targets)`
- `schema.Requires(source, requirement)`
- `schema.Equal(a, b)`, `schema.NotEqual(a, b)`, `schema.LessThan(a, b)`, `schema.LessThanOrEqual(a, b)`, `schema.GreaterThan(a, b)`, `schema.GreaterThanOrEqual(a, b)`

Other methods:

- `schema.add(*fields: Field) -> Self` — registers one or more independently-constructed fields
- `schema.validate(data: dict) -> dict` — validates a raw mapping, returns the validated data
- `schema.load(path: str | PathLike) -> dict` — reads and validates a TOML file
- `schema.template(path, *, overwrite=False, parents=True) -> None` — writes a commented `.toml` template

### Field types

All field constructors share the signature `(name, description, /, *, required=False, default=None, ...)`.

| Field | Extra parameters |
| --- | --- |
| `String` | `min_length`, `max_length`, `pattern` |
| `Literal` | `*values` (positional, at least one) |
| `Integer` | `minimum`, `maximum` |
| `Float` | `minimum`, `maximum` |
| `Boolean` | — |
| `Date` | — |
| `Time` | naive `datetime.time` only |
| `LocalDateTime` | naive `datetime.datetime` only |
| `OffsetDateTime` | timezone-aware `datetime.datetime` only |
| `Array` | `element: Field`, `min_length`, `max_length` |
| `ArrayOfTables` | `schema: Schema` (positional) |

### `ConfigurationError`

A `ValueError` subclass raised by `validate()`/`load()`. Exposes a `.path` property identifying where validation failed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
