Implement a Markdown configuration specification generator for the existing `confflow` configuration model.

The goal is to replace the current template-oriented documentation output with a human-readable Markdown reference that explains how users should construct their own TOML configuration.

Do not redesign the existing configuration, field, schema, section, array, map, or rule interfaces unless strictly necessary. The renderer must work from the metadata that already exists on those objects.

## Public API

Add an API along these lines:

```python
configuration.specification(
    path,
    overwrite=True,
)
```

Use the project's existing naming/style conventions if a slightly different signature fits better.

The generated file should be Markdown.

## Important rendering rule

Only document information that is explicitly represented by the existing configuration model.

Do not inspect, parse, or infer arbitrary logic from custom `validate()` implementations.

For example:

```python
class Email(Text):
    ...
```

must be documented using the underlying field type `Text` and the normal metadata inherited/configured through `Text`.

If an `Email` instance has:

```python
minimum_length=5
```

render that constraint.

Do not infer constraints such as "must contain @" from the custom `validate()` method.

Likewise, a custom `Port(Number)` should be rendered as type `Number` unless its numeric restrictions are explicitly represented by the normal field metadata.

## Overall Markdown structure

Start with the configuration name and description:

```md
# Application Configuration Specification

Comprehensive TOML configuration example.

Demonstrates every supported TOML-facing feature.
```

Each top-level section should then look like:

```md
## Account | optional

`[account]`

Account identity settings.

| Field | Description | Type | Required | Default | Constraints |
|---|---|---|---:|---|---|
| ... |
```

Use horizontal separators between major top-level sections:

```md
---
```

## Section headings

A section heading contains:

```md
## <human-readable name> | required
```

or:

```md
## <human-readable name> | optional
```

Immediately below it, render the TOML syntax in inline-code formatting:

```md
`[account]`
```

Then render the section/schema description.

Example:

```md
## Runtime | optional

`[runtime]`

Runtime behavior settings.
```

Only the TOML syntax itself should use inline-code formatting.

Do not write:

```md
`[[servers]]` | `1–3 entries`
```

Instead write:

```md
`[[servers]]` | 1–3 entries
```

## Field table

For ordinary schemas, use this table:

```md
| Field | Description | Type | Required | Default | Constraints |
|---|---|---|---:|---|---|
```

Each field gets exactly one row.

Example:

```md
| `username` | Account username. | Text | yes | — | • minimum length: `3`<br>• maximum length: `32`<br>• pattern: `[a-z][a-z0-9_]*` |
```

Use:

- `yes` / `no` for required state.
- `—` when there is no default.
- TOML-style values for defaults.
- inline code for field names, patterns, literal values, defaults, dates, etc.

If a field description contains multiple lines, render them using `<br>`:

```md
| `email` | Account email address.<br>Used for account notifications. | Text | yes | `"admin@example.com"` | ... |
```

## Field type rendering

Render the underlying built-in field type.

Examples:

- `Text`
- `Number`
- `Decimal`
- `Boolean`
- `OffsetDateTime`
- `LocalDateTime`
- `LocalDate`
- `LocalTime`

For literal fields, still render the underlying value type:

```text
TextLiteral -> Text
NumberLiteral -> Number
DecimalLiteral -> Decimal
BooleanLiteral -> Boolean
OffsetDateTimeLiteral -> OffsetDateTime
LocalDateTimeLiteral -> LocalDateTime
LocalDateLiteral -> LocalDate
LocalTimeLiteral -> LocalTime
```

The literal choices belong in `Constraints`.

Custom subclasses should likewise resolve to their supported base field type if that information is available through the existing class hierarchy.

For example:

```text
Email(Text) -> Text
Port(Number) -> Number
```

Do not document arbitrary custom validator behavior.

## Constraints

Each constraint must appear on its own bullet-like line inside the table cell.

Use:

```md
• minimum length: `3`<br>• maximum length: `32`
```

Do not combine constraints with semicolons.

Render only constraints that are actually configured.

Examples:

```md
• minimum: `0`
•