# confflow package structure

Snapshot of `src/confflow/` as of 2026-10-01. Generated caches are excluded.

```text
confflow/
├── __init__.py
├── core/
    ├── __init__.py
    ├── types.py
    ├── definitions/
    │   ├── __init__.py
    │   ├── base.py
    │   ├── boolean.py
    │   ├── string.py
    │   ├── constraints/
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   ├── float.py
    │   │   ├── integer.py
    │   │   ├── literal.py
    │   │   ├── local_date.py
    │   │   ├── local_date_time.py
    │   │   ├── local_time.py
    │   │   ├── offset_date_time.py
    │   │   └── string.py
    │   ├── date_time/
    │   │   ├── __init__.py
    │   │   ├── local_date.py
    │   │   ├── local_date_time.py
    │   │   ├── local_time.py
    │   │   └── offset_date_time.py
    │   └── numbers/
    │       ├── __init__.py
    │       ├── float.py
    │       └── integer.py
    ├── errors.py
    └── schemas/
        ├── __init__.py
        ├── base.py
        ├── mapping.py
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
        ├── scalars/
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
        └── table/
            ├── __init__.py
            └── constraints/
                ├── __init__.py
                ├── at_least_one_of.py
                ├── at_most_one_of.py
                ├── base.py
                ├── compare.py
                ├── equal.py
                ├── exactly_one_of.py
                ├── not_equal.py
                ├── required_together.py
                └── requires.py
├── loader/
│   └── __init__.py
├── py.typed
└── renderer/
    ├── __init__.py
    └── markdown/
        ├── __init__.py
        ├── anchors.py
        ├── constraints.py
        ├── renderer.py
        └── toml.py
```

## How the package fits together

- `confflow.core.schemas` exports the schema classes used to describe and validate named configuration entries. The package root does not currently re-export them.
- `core/schemas/base.py` defines the common `Schema` interface: a name, optional description, optional-entry flag, and `validate(value)` method.
- `core/schemas/scalars/` describes individual Boolean, string, number, and date/time entries. Each scalar delegates value checks to a matching type in `core/definitions/`.
- `core/definitions/` defines individual value types and applies their constraints; `numbers/` and `date_time/` group the numeric and date/time definitions.
- `core/definitions/constraints/` contains reusable value checks such as literal value sets, ranges, string length and patterns, and the float not-NaN constraint. `core/schemas/table/constraints/` contains constraints for relationships between table entries.
- Every table constraint exposes its referenced field names through `constraint.fields`, alongside its `NAME`, so tables and renderers can inspect constraints without knowing their concrete type.
- `core/schemas/arrays/` validates lists, including typed items, nested arrays, and tables. `mapping.py` validates mapping keys and values; `table/` combines named schemas, checks required entries, and rejects undeclared keys.
- `core/errors.py` defines `SchemaError` for invalid schema or constraint configuration and `ValidationError` for invalid runtime values. `ValidationError` preserves the offending value, constraint, expected rule, and nested field/index path while remaining compatible with `ValueError` handlers.
- `core/types.py` contains shared value types; `py.typed` marks the package as typed. Validation errors gain context as they propagate through definitions and nested schemas.
- `loader/` remains a package placeholder. `renderer/markdown/` renders a completed root `Table` as a Markdown configuration reference; its helper modules format field anchors, definition and table constraints, and TOML default values. Use `MarkdownRenderer().render(root_table)` to generate the reference.

Table construction checks child-name uniqueness and verifies that every table constraint references declared child schemas; invalid configuration raises `SchemaError` immediately. Validation starts with a schema's `validate(value)` method. Definitions attach constraint and value details; tables, arrays, and mappings add field names, indices, and keys to the `ValidationError` path as runtime failures propagate. This snapshot describes the current package only, not an entire configuration-loading pipeline.
