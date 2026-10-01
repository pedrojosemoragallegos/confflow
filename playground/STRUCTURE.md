# confflow package structure

Snapshot of `src/confflow/` as of 2026-10-01. Generated caches are excluded.

```text
confflow/
├── __init__.py
├── py.typed
└── core/
    ├── __init__.py
    ├── types.py
    ├── definitions/
    │   ├── __init__.py
    │   ├── _validators.py
    │   ├── base.py
    │   ├── boolean.py
    │   ├── exceptions.py
    │   ├── string.py
    │   ├── numbers/
    │   │   ├── __init__.py
    │   │   ├── _validators.py
    │   │   ├── float.py
    │   │   └── integer.py
    │   └── time/
    │       ├── __init__.py
    │       ├── _validators.py
    │       ├── local_date.py
    │       ├── local_date_time.py
    │       ├── local_time.py
    │       └── offset_date_time.py
    └── schemas/
        ├── __init__.py
        ├── _validators.py
        ├── base.py
        ├── exceptions.py
        ├── mapping.py
        ├── table.py
        ├── arrays/
        │   ├── __init__.py
        │   ├── base.py
        │   ├── boolean.py
        │   ├── float.py
        │   ├── integer.py
        │   ├── local_date.py
        │   ├── local_date_time.py
        │   ├── local_time.py
        │   ├── nested.py
        │   ├── offset_date_time.py
        │   ├── string.py
        │   └── table.py
        └── scalars/
            ├── __init__.py
            ├── base.py
            ├── boolean.py
            ├── float.py
            ├── integer.py
            ├── local_date.py
            ├── local_date_time.py
            ├── local_time.py
            ├── offset_date_time.py
            └── string.py
```

## How the package fits together

- `confflow.core.schemas` exports the schema classes used to describe and validate named configuration entries. The package root does not currently re-export them.
- `core/schemas/base.py` defines the common `Schema` interface: a name, optional description, optional-entry flag, and `validate(value)` method.
- `core/schemas/scalars/` describes individual Boolean, string, number, and date/time entries. Each scalar delegates value checks to a matching type in `core/definitions/`.
- `core/definitions/` holds reusable validators for individual values; `numbers/` and `time/` group the numeric and date/time types.
- `core/schemas/arrays/` validates lists, including typed items, nested arrays, and tables. `mapping.py` validates mapping keys and values; `table.py` combines named schemas into a table and checks required entries.
- `core/types.py` contains shared value types; `py.typed` marks the package as typed. Validator helpers and exception types live beside the definitions and schemas that use them.

Validation starts with a schema's `validate(value)` method. A table validates each named entry, and scalar or collection schemas then validate the corresponding value. This snapshot describes the current package only, not an entire configuration-loading pipeline.