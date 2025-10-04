# ConfFlow

A Python library for schema-based YAML configuration management with built-in validation, constraints, and type safety.

## Features

- **Type-Safe Configuration**: Support for all common data types
  - Scalars: `str`, `int`, `float`, `bool`, `datetime`, `bytes`
  - Lists: `list[str]`, `list[int]`, `list[float]`, `list[bool]`, `list[datetime]`, `list[bytes]`

- **Comprehensive Validation**: Built-in constraint system
  - String constraints: min/max length, regex patterns, enum values
  - Numeric constraints: greater/less than (or equal), ranges
  - List constraints: min/max length, item-level validation

- **Nested Schemas**: Hierarchical configuration structures with unlimited nesting

- **Group Constraints**: Advanced validation logic
  - `OneOf`: Exactly one schema from a group must be present
  - `AnyOf`: At least one schema from a group must be present

- **Template Generation**: Automatic YAML template creation with inline documentation

- **Default Values**: Support for defaults at all levels

## Installation

```bash
pip install confflow
```

## Quick Start

### 1. Define Your Schema

```python
from confflow import Manager
from confflow.schema import Schema
from confflow.schema.fields import StringField, IntegerField, BooleanField
from confflow.schema.groups import OneOf

# Create a schema
database_schema = Schema(
    "database",
    description="Database configuration"
).add(
    StringField(
        "host",
        description="Database host",
        default="localhost",
        min_length=1,
        max_length=255
    )
).add(
    IntegerField(
        "port",
        description="Database port",
        default=5432,
        gt=0,
        le=65535
    )
).add(
    BooleanField(
        "ssl_enabled",
        description="Enable SSL",
        default=True
    )
)

# Create configuration manager
manager = Manager(database_schema)
```

### 2. Generate Configuration Templates

```python
# Generate individual template files for each schema
manager.create_templates("./templates")
```

This creates separate YAML template files with inline documentation:

**`templates/database_template.yml`:**
```yaml
database:
  # Database host
  # type: str
  # constraints:
  #  - Minimum length = 1
  #  - Maximum length = 255
  host: localhost
  # Database port
  # type: int
  # constraints:
  #  - Greater than: 0
  #  - Less than or equal: 65535
  port: 5432
  # Enable SSL
  # type: bool
  ssl_enabled: True
```

### 3. Load and Validate Configuration

```python
# Load configuration from one or more files
config = manager.load("config.yml")

# Or load from multiple files (later files override earlier ones)
config = manager.load("base.yml", "environment.yml", "overrides.yml")

# Access configuration values
print(config.database.host)  # "localhost"
print(config.database.port)  # 5432
print(config.database.ssl_enabled)  # True

# Or use dictionary-style access
print(config["database"]["host"])  # "localhost"
```

## Advanced Usage

### Multiple Schemas and Template Generation

```python
# Create multiple schemas
database_schema = Schema("database", description="Database configuration").add(
    StringField("host", description="DB host", default="localhost")
).add(
    IntegerField("port", description="DB port", default=5432)
)

api_schema = Schema("api", description="API configuration").add(
    StringField("base_url", description="API base URL", default="http://localhost:8000")
).add(
    IntegerField("timeout", description="Request timeout (seconds)", default=30)
)

# Initialize manager with multiple schemas
manager = Manager(database_schema, api_schema)

# Generate separate template files for each schema
manager.create_templates("./config/templates")
# Creates:
#   - ./config/templates/database_template.yml
#   - ./config/templates/api_template.yml

# Load configuration from multiple template files
config = manager.load(
    "./config/templates/database_template.yml",
    "./config/templates/api_template.yml"
)
```

### Nested Schemas

```python
app_schema = Schema(
    "app",
    description="Application configuration"
).add(
    StringField("name", description="App name", default="MyApp")
).add(
    Schema("database", description="Database settings")
    .add(StringField("host", description="DB host", default="localhost"))
    .add(IntegerField("port", description="DB port", default=5432))
)
```

### Group Constraints

```python
from confflow.schema.groups import OneOf, AnyOf

# OneOf: Exactly one cloud provider must be configured
cloud_schema = Schema("config", description="Cloud configuration").add(
    OneOf(
        Schema("aws", description="AWS config")
        .add(StringField("region", description="AWS region", default="us-east-1")),
        
        Schema("gcp", description="GCP config")
        .add(StringField("project", description="GCP project", default="my-project")),
        
        Schema("azure", description="Azure config")
        .add(StringField("subscription", description="Subscription ID"))
    )
)

# AnyOf: At least one observability tool must be enabled
observability_schema = Schema("config", description="Config").add(
    AnyOf(
        Schema("logging", description="Logging config")
        .add(StringField("level", description="Log level", default="INFO")),
        
        Schema("monitoring", description="Monitoring config")
        .add(StringField("provider", description="Provider", default="prometheus")),
        
        Schema("tracing", description="Tracing config")
        .add(StringField("backend", description="Backend", default="jaeger"))
    )
)
```

### Field Constraints

```python
from confflow.schema.fields import (
    StringField, IntegerField, FloatField,
    Stringlist, Integerlist, Floatlist
)

schema = Schema("app", description="Application").add(
    # String with regex and enum
    StringField(
        "environment",
        description="Deployment environment",
        default="development",
        enum=["development", "staging", "production"]
    )
).add(
    # Integer with range
    IntegerField(
        "max_connections",
        description="Max connections",
        default=100,
        ge=1,
        le=1000
    )
).add(
    # Float with precision
    FloatField(
        "threshold",
        description="Threshold percentage",
        default=95.5,
        ge=0.0,
        le=100.0
    )
).add(
    # String list with item validation
    Stringlist(
        "allowed_origins",
        description="CORS origins",
        default=["http://localhost:3000"],
        min_length=1,
        max_length=10,
        item_regex=r"^https?://"
    )
).add(
    # Integer list with item constraints
    Integerlist(
        "port_ranges",
        description="Allowed ports",
        default=[8000, 8080, 8443],
        min_length=1,
        max_length=20,
        item_gt=0,
        item_le=65535
    )
)
```

### Custom Constraints

```python
from confflow.schema.constraint import Constraint, ValidationError

class CustomEmailConstraint(Constraint[str]):
    def __call__(self, value: str) -> str:
        if not value.endswith("@company.com"):
            raise ValidationError(f"{value} must be a company email")
        return value
    
    def __repr__(self) -> str:
        return "CustomEmailConstraint()"
    
    def to_formatted_string(self, indent: int = 0) -> str:
        return "Must end with @company.com"

# Use in field
StringField(
    "email",
    CustomEmailConstraint(),
    description="Company email",
    regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)
```

### Validation from Dictionary

```python
# Validate dictionary data directly
data = {
    "database": {
        "host": "db.example.com",
        "port": 5432,
        "ssl_enabled": True
    }
}

config = manager.loads(data)
```

### Loading from File Buffers

```python
# Load from file-like objects
with open("config.yml") as f:
    config = manager.load(f)

# Mix file paths and buffers
with open("overrides.yml") as f:
    config = manager.load("base.yml", f, "local.yml")
```

## API Reference

### Manager

```python
class Manager:
    """
    Manages multiple configuration schemas for validation and template generation.
    """
    
    def __init__(self, *schemas: Schema) -> None:
        """
        Initialize manager with one or more schemas.
        
        Raises:
            ValueError: If no schemas provided or duplicates detected.
        """
    
    def validate(self, data: dict) -> None:
        """Validate configuration data against all schemas."""
    
    def loads(self, data: dict) -> Config:
        """Load and validate configuration from dictionary."""
    
    def load(self, *filepaths_or_buffers: str | PathLike | IO) -> Config:
        """
        Load and merge configuration from multiple files or buffers.
        
        Args:
            *filepaths_or_buffers: One or more file paths or file-like buffers.
        
        Returns:
            Config: Validated merged configuration.
        
        Raises:
            ValueError: If no paths provided or validation fails.
        """
    
    def create_templates(self, directory: str | PathLike) -> None:
        """
        Create individual template YAML files for each schema.
        
        Args:
            directory: Directory where template files will be created.
        """
```

### Schema

```python
class Schema:
    def __init__(self, name: str, description: str) -> None: ...
    def add(self, item: Schema | Group | Field) -> Self: ...
    def validate(self, data: dict) -> None: ...
```

### Fields

**Scalar Fields:**

- `StringField(name, *, description, default, min_length, max_length, regex, enum)`
- `IntegerField(name, *, description, default, gt, ge, lt, le)`
- `FloatField(name, *, description, default, gt, ge, lt, le)`
- `BooleanField(name, *, description, default)`
- `DateField(name, *, description, default)`
- `BytesField(name, *, description, default)`

**List Fields:**

- `Stringlist(name, *, description, default, min_length, max_length, item_min_length, item_max_length, item_regex, item_enum)`
- `Integerlist(name, *, description, default, min_length, max_length, item_gt, item_ge, item_lt, item_le)`
- `Floatlist(name, *, description, default, min_length, max_length, item_gt, item_ge, item_lt, item_le)`
- `Booleanlist(name, *, description, default, min_length, max_length)`
- `Datelist(name, *, description, default, min_length, max_length)`
- `Byteslist(name, *, description, default, min_length, max_length)`

### Groups

- `OneOf(*schemas)`: Exactly one schema must be present
- `AnyOf(*schemas)`: At least one schema must be present

## Error Handling

ConfFlow raises `ValueError` exceptions with descriptive messages for validation failures:

```python
try:
    config = manager.load("config.yml")
except ValueError as e:
    print(f"Configuration validation failed: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.