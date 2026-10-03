# confflow

[![PyPI version](https://img.shields.io/pypi/v/confflow)](https://pypi.org/project/confflow/)
[![Python Versions](https://img.shields.io/pypi/pyversions/confflow)](https://pypi.org/project/confflow/)
[![Downloads](https://pepy.tech/badge/confflow)](https://pepy.tech/project/confflow)
[![Wheel](https://img.shields.io/pypi/wheel/confflow)](https://pypi.org/project/confflow/)

Confflow defines schemas for TOML configuration files, generates annotated templates, and validates loaded values.

Applications often need configuration files that are understandable to edit and checked before use. Confflow lets you describe fields, nested tables, constraints, and secrets in Python, then use that schema to render a TOML template and validate configuration as it is loaded. It supports Python 3.11 and later, is typed, and processes files locally.

## Features

- Define schemas for TOML scalar values, arrays, nested tables, mappings, and arrays of tables.
- Validate field types, required and optional values, bounds, allowed values, and relationships between fields.
- Generate commented TOML templates with field descriptions, defaults, and constraints.
- Resolve scalar values from environment variables and redact marked secrets in representations and validation errors.
- Return loaded mappings as read-only mappings and arrays as tuples.

## Installation

```bash
pip install confflow
```

Requires Python 3.11 or later.

## Quick Start

```python
from confflow import Configuration
from confflow.schemas import Integer, String

config = Configuration(
    "Application",
    "Application configuration",
    String(
        "environment",
        "Deployment environment",
        literal=["development", "production"],
        default="production",
    ),
    Integer("port", "HTTP port", minimum=1, maximum=65535, default=8080),
)

config.template("config.toml")
settings = config.load("config.toml")
print(settings["port"])
```

Save this as a Python file and run it after installing Confflow. It writes an annotated `config.toml` and loads and validates it.

## Usage

Define fields with `confflow.schemas`, add built-in table constraints from `confflow.constraints`, and subclass a typed `*Constraint` to implement application-specific validation. The module names custom value-validator bases explicitly (for example, `StringConstraint`) and exposes `ValueConstraint` and `TableConstraint` as their shared bases. This example checks an email address, relates worker limits, and resolves a secret from the environment.

Save as `app.py`:

```python
import re

from confflow import Configuration
from confflow.constraints import (
    AtMostOneOf,
    LessThanOrEqual,
    Requires,
    StringConstraint,
)
from confflow.schemas import Integer, String, Table


class Email(StringConstraint):
    def __call__(self, value: str, /) -> None:
        if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value) is None:
            raise ValueError("value is not a valid email address")


server = Table(
    "server",
    "HTTP server settings",
    Integer("minimum_workers", "Minimum workers", minimum=1, default=2),
    Integer("maximum_workers", "Maximum workers", maximum=128, default=16),
    LessThanOrEqual("minimum_workers", "maximum_workers"),
)

notifications = Table(
    "notifications",
    "Notification destination",
    String("email", "Contact email", Email(), optional=True),
    String("webhook", "Webhook URL", optional=True),
)

account = Table(
    "account",
    "Optional deployment credentials",
    String("username", "Username", optional=True),
    String("password", "Password", optional=True, secret=True),
    String("token", "API token", optional=True, secret=True),
    Requires("username", "password"),
    AtMostOneOf("password", "token"),
    optional=True,
)

config = Configuration(
    "Application",
    "Application configuration",
    String("environment", "Deployment environment", default="production"),
    server,
    notifications,
    account,
)

config.template("config.example.toml")
settings = config.load("config.toml")
print(settings["notifications"])
```

Custom constraints implement `__call__` and raise `ValueError` for invalid values. Optionally implement `__str__` to describe the constraint in generated template comments. Within a `Table`, declare all fields before its constraints; constraint operands refer to immediate child field names.

Save this as `config.toml`:

```toml
environment = "production"

[server]
minimum_workers = 2
maximum_workers = 8

[notifications]
email = "ops@example.com"

[account]
username = "deploy"
password = "$APP_PASSWORD"
```

Run both files from the same directory:

```bash
export APP_PASSWORD='replace-with-a-secret'
python app.py
```

The normal workflow is to call `config.template(...)` to create a starter TOML file, edit it, then call `config.load(path)` to parse and validate it. Template generation accepts `overwrite=True` to replace an existing file and `parents=True` to create missing parent directories. By default, an existing destination is not overwritten.

Templates can contain unfilled assignments such as `email =`. Supply a value or remove an optional assignment before loading; unfilled assignments are not valid TOML.

## How It Works

1. Define a schema using scalar, array, table, and constraint objects.
2. Generate a commented TOML template from the schema, including any declared defaults.
3. Load a TOML file; Confflow resolves supported environment references, validates the values against the schema, and returns read-only configuration data.

## Configuration

Configuration files use TOML. A schema distinguishes required fields from optional ones and can define scalar defaults, value constraints, and relationships between table fields. Defaults are written into generated templates; required values still need to be present when loading a file.

For scalar fields, a TOML string containing exactly `$NAME` is replaced with the value of the `NAME` environment variable and converted to the schema's scalar type. Use `$$NAME` when the intended value is the literal string `$NAME`. Referencing an unset variable or providing a value that cannot be converted raises a validation error.

Mark sensitive scalar fields with `secret=True`. Secret values are omitted from generated template defaults and redacted in mapping representations and validation errors.

## Development

The project uses [uv](https://docs.astral.sh/uv/) for dependency management. With Python 3.11 or later installed:

```bash
uv sync
uv run ruff check src
uv run ty check src/confflow
```

## Project Structure

- `src/confflow/` — public API modules, TOML loader and template renderer.
- `src/confflow/core/` — schema, value-definition and validation implementations.
- `example/` — example application schema and generated TOML template.

## License

[MIT](LICENSE)
