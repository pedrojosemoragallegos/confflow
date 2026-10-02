# confflow package structure

Snapshot of `src/confflow/` as of 2026-10-02. Generated caches are excluded.

```text
confflow/
├── __init__.py
├── config.py
├── render.py
├── core/
│   ├── __init__.py
│   ├── errors.py
│   ├── types.py
│   ├── definitions/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── boolean.py
│   │   ├── string.py
│   │   ├── constraints/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── boolean.py
│   │   │   ├── float.py
│   │   │   ├── integer.py
│   │   │   ├── literal.py
│   │   │   ├── local_date.py
│   │   │   ├── local_date_time.py
│   │   │   ├── local_time.py
│   │   │   ├── offset_date_time.py
│   │   │   └── string.py
│   │   ├── date_time/
│   │   │   ├── __init__.py
│   │   │   ├── local_date.py
│   │   │   ├── local_date_time.py
│   │   │   ├── local_time.py
│   │   │   └── offset_date_time.py
│   │   └── numbers/
│   │       ├── __init__.py
│   │       ├── float.py
│   │       └── integer.py
│   └── schemas/
│       ├── __init__.py
│       ├── base.py
│       ├── mapping.py
│       ├── arrays/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── boolean.py
│       │   ├── float.py
│       │   ├── integer.py
│       │   ├── local_date.py
│       │   ├── local_date_time.py
│       │   ├── local_time.py
│       │   ├── nested.py
│       │   ├── offset_date_time.py
│       │   ├── string.py
│       │   └── table.py
│       ├── scalars/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── boolean.py
│       │   ├── float.py
│       │   ├── integer.py
│       │   ├── local_date.py
│       │   ├── local_date_time.py
│       │   ├── local_time.py
│       │   ├── offset_date_time.py
│       │   └── string.py
│       └── table/
│           ├── __init__.py
│           ├── base.py
│           └── constraints/
│               ├── __init__.py
│               ├── at_least_one_of.py
│               ├── at_most_one_of.py
│               ├── base.py
│               ├── _validation.py
│               ├── comparision/
│               │   ├── __init__.py
│               │   ├── base.py
│               │   ├── greater_than.py
│               │   ├── greater_than_or_equal.py
│               │   ├── less_than.py
│               │   └── less_than_or_equal.py
│               ├── equal.py
│               ├── exactly_one_of.py
│               ├── not_equal.py
│               ├── required_together.py
│               └── requires.py
└── py.typed
```

## How the package fits together

- `confflow.core.schemas` exports the schema classes used to describe and validate named configuration entries. The package root does not re-export them.
- `core/schemas/base.py` defines the common `Schema` interface: a name, optional description, optional-entry flag, and `validate(value)` method.
- `core/schemas/scalars/` describes individual Boolean, string, number, and date/time entries. Each scalar delegates value checks to a matching type in `core/definitions/`.
- `core/definitions/` defines individual value types and applies their constraints; `numbers/` and `date_time/` group the numeric and date/time definitions.
- `core/definitions/constraints/` contains reusable value checks such as literal value sets, ranges, string length and patterns, and the float not-NaN constraint. `core/schemas/table/constraints/` contains constraints for relationships between table entries.
- `core/definitions/constraints/base.py` defines the generic `Constraint[T]`. Each type-specific constraint module starts with its abstract typed base: `Boolean`, `String`, `Integer`, `Float`, `LocalDate`, `LocalTime`, `LocalDateTime`, or `OffsetDateTime`. All are exported by `confflow.core.definitions.constraints`. Custom constraints inherit the matching base and implement `__call__(value)` to raise an error for invalid values; the playground's `Email` demonstrates this using `String`. The date/time bases specialize Python value types without adding timezone checks; value definitions enforce those checks.
- Every table constraint exposes its referenced field names through `constraint.fields`, so tables can validate constraint references and values. Constraints do not declare `NAME`: diagnostic identifiers come from snake_case class names (for example, `LessThanOrEqual` becomes `less_than_or_equal`). Leading and trailing underscores are removed. Template text remains independently controlled by `__str__`.
- `core/schemas/arrays/` validates lists, including typed items, nested arrays, and tables. `mapping.py` validates mapping keys and values; `table/base.py` implements `Table`, which combines named schemas, checks required entries, and rejects undeclared keys. `table/__init__.py` re-exports `Table`.
- `core/errors.py` defines `SchemaError` for invalid schema or constraint configuration and `ValidationError` for invalid runtime values. `ValidationError` preserves the offending value, constraint, expected rule, and nested field/index path while remaining compatible with `ValueError` handlers.
- `core/types.py` contains shared value types; `py.typed` marks the package as typed.

Table construction checks child-name uniqueness and verifies that every table constraint references declared child schemas; invalid configuration raises `SchemaError` immediately. Validation starts with a schema's `validate(value)` method. Definitions attach constraint and value details; tables, arrays, and mappings add field names, indices, and keys to the `ValidationError` path as runtime failures propagate.

Tables accept both schemas and table constraints as positional items:

```python
Table(
    "authentication",
    "Authentication configuration",
    String("username", "", optional=True),
    String("password", "", optional=True),
    Requires("username", "password"),
    optional=True,
)
```

The signature is `Table(name, description, /, *items, optional=False)`.
All schemas must precede all constraints; a schema after a constraint or an item
of any other type raises `SchemaError`. Order is preserved within each group,
exposed through the existing `schemas` and `constraints` properties.
The `constraints=` keyword is no longer accepted.
The table constraint `base.py` defines only the constraint interface; shared
constructor checks for operand names, arity, and uniqueness live in `_validation.py`.

Ordered comparisons use `LessThan(left, right)`, `LessThanOrEqual(left, right)`,
`GreaterThan(left, right)`, and `GreaterThanOrEqual(left, right)`, with child names
as operands. For example, `LessThanOrEqual("minimum_workers", "maximum_workers")`.
They validate only when both operands are present; incomparable values fail
validation. `Equal` and `NotEqual` handle equality and inequality.
The operator-string `Compare` API has been removed.
The `comparision/` package exposes the abstract `Comparision` base in `base.py`.
It owns operand construction, `left`, `right`, `fields`, and debug representation.
Concrete subclasses implement `__call__` and optionally `__str__` normally;
there is no operator constant, operator property, or comparison-function hook.
The existing table constraint package re-exports the base and all four classes.

## Configuration documents

`config.py` owns document identity, composition, validation, and filesystem
operations. `render.py` owns pure template text generation through
`render_template(name, description, schemas) -> str`, including metadata, TOML
values, ordering, and spacing. It performs no file operations or validation.

The package root exports `Configuration(name, description, /, *schemas)`. A configuration
has read-only `name`, `description`, and `schemas` properties, and composes both
loose fields and tables. Names follow the existing schema name rules. Empty
descriptions are stored as `None`, matching schemas.

- `validate(value: Mapping[str, object], /) -> None` delegates to the existing
  table validator without root-level constraints.
- `template(destination: str | Path, *, overwrite=False, parents=False) -> Path`
  writes a semi-valid TOML template with commented documentation and missing-value
  examples. After `Path` normalization, only
  existing directories are directory destinations: they receive
  `<config-name-lowercase>.toml`. Every other destination is the exact file path,
  even if suffixless. `parents=True` creates the final file's parent directories;
  it does not turn a nonexistent destination into a directory. Exclusive creation
  is the default; `overwrite=True` permits replacement.
- `load(source: str | Path) -> Mapping[str, object]` opens the file in binary mode,
  parses it with Python 3.11's `tomllib`, validates it, and returns the parsed
  mapping unchanged. Missing required fields fail even if they have defaults.
  Missing optional fields succeed; no defaults are inserted. Parse and filesystem
  errors retain their standard exceptions; value errors use `ValidationError`.

Templates use the following format, with exactly one blank line after the config
description and before each table section, and no blank lines between fields or
after table headers:

```toml
# Application configuration

# Application name
# Required | string | "example"
name = "example"

# Server settings
# Required
[server]
# Server port
# Required | integer | 8080
# Value must be between 1 and 65535
port = 8080
```

Loose fields precede table sections, preserving order within each group, both at
the root and inside tables. Nested tables use dotted headers such as
`[server.limits]`. Table arrays are also table sections and use
`[[backends]]`. All non-table fields without a concrete default have active
blank assignments, such as `port =` or `contact_email =`, regardless of
optionality. This includes arrays (not active empty collections). Fields with
concrete defaults have active assignments, including inside optional ordinary
tables. All ordinary table and mapping headers remain active, including optional
and nested tables.
Optional/Required is informational metadata in templates, not a commenting rule;
runtime presence validation remains unchanged.
Documentation is not double-commented. Every table array and mapping,
required or optional, has exactly one commented sample block. Table arrays
include metadata
`Required | array of tables` or `Optional | array of tables`. The frame uses exactly
`# --- <copy block> ---` and `# --- </copy block> ---`, without an introductory
copy instruction.
Mapping sections show one scalar key assignment or one keyed table with its
fields, depending on the mapped value schema. Mapping sample blocks use the
placeholder key `<key>` and the frame
`# --- <copy this block> ---` / `# --- </copy this block> ---`, without an
additional copy instruction. The content
between the markers has one extra `# ` layer: headers and assignments are
commented once, while documentation is commented twice. Remove one layer to
activate the sample while preserving its documentation comments. Nested copy
blocks retain their own comment layer until individually uncommented.
No blank lines separate fields, including inside samples. One blank line separates
tables/table sections. No blank line separates structure metadata from its
opening copy-block marker.
Users copy, uncomment one layer, fill in missing values, and duplicate the block
for additional items.
Templates containing active blank assignments are intentionally semi-valid:
fill in those assignments before parsing TOML. Templates can still fail schema validation
until required values and table relationships are supplied. Loading never inserts
missing defaults. Defaults are rendered
with the existing `tomlkit` dependency as TOML values, not Python representations.
Descriptions are omitted when absent, except for the config header's description
line. Every description/metadata line is commented, including multiline text.

Metadata uses `Required | type | value` (omitting absent defaults), with
TOML type names such as `string`, `boolean`, `local date-time`,
`array of string`, and `table`. Each visible constraint occupies a separate
comment line.
Field constraints use sentences such as `Length must be between 1 and 64`,
`Value must be at least 1`, and `Value must be one of "development" or "production"`.
Patterns use `Value must match the pattern "[A-Z]+"`. Unbounded ranges and lengths
have no template text. Table rules use
sentences with quoted names, such as `"low" must be <= "high"`,
`"username" requires "password" to be provided`, and
`At most one of "password" or "token" may be provided`.
Constraint `__str__` methods provide all human-readable template text; the renderer
uses `str(constraint)` and skips empty strings entirely, without placeholder comment
lines. Both value and table constraints can override `__str__` to return custom text
or `""` to hide their metadata. Both bases return `""` by default; subclasses
opt in to visible metadata by overriding `__str__`. Parameterized built-in
constraints supply readable text; `NotNaN` and the playground's `Email` keep the
empty base representation and do not appear in templates. `__repr__` remains
separate developer/debug output and is never used for template rendering.
Richer examples for nested arrays and custom human-readable constraint
documentation would need an explicit metadata design before expanding this
format. No global constraints, cross-table validation, merging, or runtime
fallback behavior are provided.

`example.py` demonstrates every exported scalar and array schema, scalar- and
table-valued mappings, and table arrays, then generates a template and loads a
separate populated TOML file in `output/`. Its table constraints cover presence
rules (`Requires`, `Forbids`, `RequiredTogether`, `AtLeastOneOf`, `AtMostOneOf`,
and `ExactlyOneOf`), equality rules (`Equal` and `NotEqual`), and all four
ordered comparisons (`LessThan`, `LessThanOrEqual`, `GreaterThan`, and
`GreaterThanOrEqual`). Each ordered comparison has its own operand pair in the
`comparison_examples` section so the examples show distinct rules without
stacking redundant constraints on the same fields.
