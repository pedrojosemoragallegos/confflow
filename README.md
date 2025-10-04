# ConfFlow

An extremely fast Python library for schema-based YAML configuration management with built-in validation, constraints, and type safety.

## Features

- **Type-Safe Configuration**: Support for all common data types
  - Scalars: `str`, `int`, `float`, `bool`, `datetime`, `bytes`
  - Lists: `list[str]`, `list[int]`, `list[float]`, `list[bool]`, `list[datetime]`, `list[bytes]`

- **Comprehensive Validation**: Built-in constraint system
  - String constraints: min/max length, regex patterns, enum values
  - Numeric constraints: greater/less than (or equal), ranges
  - List constraints: min/max length, item-level validation

- **Flexible Schema Organization**:
  - **Nested Schemas**: Create hierarchical configuration structures with unlimited nesting depth
  - **Multiple Independent Schemas**: Compose configurations from separate schema definitions
  - **Split Configuration Files**: Load and merge multiple YAML files into a single validated config
  - **Directory Loading**: Automatically load all `.yml` files from a directory

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
# Database configuration
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
# Load configuration from a single file
config = manager.load("config.yml")

# Or load from multiple files (later files override earlier ones)
config = manager.load("base.yml", "environment.yml", "overrides.yml")

# Or load all .yml files from a directory
config = manager.load("./config")

# Access configuration with dot notation or subscription
print(config.database.host)  # Dot notation
print(config["database"]["host"])  # Subscription
print(config.database["port"])  # Mixed!
print(config["database"].ssl_enabled)  # Also mixed!
```

## Configuration Organization Patterns

ConfFlow supports two powerful patterns for organizing your configuration:

### Pattern 1: Nested Schemas (Hierarchical Structure)

Use nested schemas when you want a single configuration file with hierarchical organization:

```python
# Create a single schema with nested structure
app_schema = Schema(
    "app",
    description="Application configuration"
).add(
    StringField("name", description="App name", default="MyApp")
).add(
    StringField("version", description="App version", default="1.0.0")
).add(
    # Nest database config inside app schema
    Schema("database", description="Database settings")
    .add(StringField("host", description="DB host", default="localhost"))
    .add(IntegerField("port", description="DB port", default=5432))
    .add(BooleanField("ssl", description="Use SSL", default=True))
).add(
    # Nest cache config inside app schema
    Schema("cache", description="Cache settings")
    .add(StringField("backend", description="Cache backend", default="redis"))
    .add(IntegerField("ttl", description="TTL in seconds", default=3600))
)

manager = Manager(app_schema)
manager.create_templates("./templates")
# Creates: ./templates/app_template.yml (single file with nested structure)
```

**Generated `app_template.yml`:**

```yaml
# Application configuration
app:
  # App name
  # type: str
  name: MyApp
  
  # App version
  # type: str
  version: 1.0.0
  
  # Database settings
  database:
    # DB host
    # type: str
    host: localhost
    
    # DB port
    # type: int
    port: 5432
    
    # Use SSL
    # type: bool
    ssl: True
  
  # Cache settings
  cache:
    # Cache backend
    # type: str
    backend: redis
    
    # TTL in seconds
    # type: int
    ttl: 3600
```

**Usage:**

```python
config = manager.load("app.yml")
print(config.app.name)           # "MyApp"
print(config.app.database.host)  # "localhost"
print(config.app.cache.backend)  # "redis"
```

### Pattern 2: Multiple Independent Schemas (Modular Structure)

Use multiple schemas when you want separate, independent configuration files that can be managed and loaded separately:

```python
# Create separate top-level schemas
database_schema = Schema(
    "database", 
    description="Database configuration"
).add(
    StringField("host", description="DB host", default="localhost")
).add(
    IntegerField("port", description="DB port", default=5432)
)

api_schema = Schema(
    "api", 
    description="API configuration"
).add(
    StringField("base_url", description="API base URL", default="http://localhost:8000")
).add(
    IntegerField("timeout", description="Request timeout (seconds)", default=30)
)

logging_schema = Schema(
    "logging",
    description="Logging configuration"
).add(
    StringField("level", description="Log level", default="INFO", enum=["DEBUG", "INFO", "WARNING", "ERROR"])
).add(
    StringField("format", description="Log format", default="json")
)

# Manager accepts multiple schemas
manager = Manager(database_schema, api_schema, logging_schema)

# Generate separate template files
manager.create_templates("./config/templates")
# Creates:
#   - ./config/templates/database_template.yml
#   - ./config/templates/api_template.yml
#   - ./config/templates/logging_template.yml
```

**Usage - Load All or Some:**

```python
# Load all configurations
config = manager.load(
    "./config/database.yml",
    "./config/api.yml", 
    "./config/logging.yml"
)

# Access each configuration section
print(config.database.host)      # "localhost"
print(config.api.base_url)       # "http://localhost:8000"
print(config.logging.level)      # "INFO"

# Or load only what you need (partial configuration)
config = manager.load("./config/database.yml", "./config/api.yml")
print(config.database.port)      # 5432
print(config.api.timeout)        # 30
# config.logging would not exist
```

### Pattern 3: Combining Both Approaches

You can mix nested and modular schemas for maximum flexibility:

```python
# Main app config with nested auth
app_schema = Schema("app", description="Application").add(
    StringField("name", default="MyApp")
).add(
    Schema("auth", description="Authentication").add(
        StringField("provider", default="oauth2")
    ).add(
        IntegerField("session_timeout", default=3600)
    )
)

# Separate database config
database_schema = Schema("database", description="Database").add(
    StringField("host", default="localhost")
)

# Separate feature flags config
features_schema = Schema("features", description="Feature flags").add(
    BooleanField("new_ui", default=False)
).add(
    BooleanField("beta_api", default=False)
)

manager = Manager(app_schema, database_schema, features_schema)

# Load configurations - mix templates and custom files
config = manager.load(
    "./templates/app_template.yml",      # Base app config with nested auth
    "./config/database.yml",             # Database config
    "./config/features_dev.yml",         # Dev-specific feature flags
    "./config/overrides.yml"             # Local overrides
)

print(config.app.name)              # "MyApp"
print(config.app.auth.provider)     # "oauth2" (nested)
print(config.database.host)         # From database.yml (modular)
print(config.features.new_ui)       # From features_dev.yml (modular)
```

### Multi-File Loading and Merging

Load and merge multiple YAML files - later files override earlier ones:

```python
# Base configuration with defaults
# base.yml:
# database:
#   host: localhost
#   port: 5432

# Environment-specific overrides
# production.yml:
# database:
#   host: prod-db.example.com
#   ssl_enabled: True

# Local development overrides
# local.yml:
# database:
#   port: 5433

# Load with override priority: base < production < local
config = manager.load("base.yml", "production.yml", "local.yml")

print(config.database.host)        # "prod-db.example.com" (from production.yml)
print(config.database.port)        # 5433 (from local.yml - overrides base)
print(config.database.ssl_enabled) # True (from production.yml)
```

### Directory Loading

Load all `.yml` files from a directory automatically:

```python
# Directory structure:
# ./config/
#   ├── database.yml
#   ├── api.yml
#   └── logging.yml

# Load all .yml files from directory (sorted alphabetically)
config = manager.load("./config")

# Equivalent to:
# config = manager.load("./config/api.yml", "./config/database.yml", "./config/logging.yml")

# Access configurations
print(config.database.host)
print(config.api.base_url)
print(config.logging.level)
```

**Note:** Directory loading is non-recursive and only loads files directly in the specified directory. Files are loaded in alphabetical order.

## Advanced Features

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

## API Reference

### Manager

The `Manager` class coordinates validation and template generation for your schemas.

**`Manager(*schemas: Schema)`**

- Initializes with one or more schemas
- Each schema becomes a top-level configuration section
- Raises `ValueError` if no schemas provided or duplicates detected

**`manager.validate(data: dict)`**

- Validates configuration data against all schemas
- Raises `ValueError` on validation failure

**`manager.loads(data: dict) -> Config`**

- Loads and validates configuration from a dictionary
- Returns a frozen `Config` dataclass

**`manager.load(*filepaths: str | Path) -> Config`**

- Loads and merges configuration from multiple files or a directory
- If a single directory path is provided, loads all `.yml` files from that directory
- Later files override earlier ones for duplicate keys
- Returns a validated `Config` object
- Raises `ValueError` if no files provided or if a directory contains no `.yml` files

**`manager.create_templates(directory: str | Path)`**

- Creates `{schema_name}_template.yml` for each schema
- Creates directory if it doesn't exist

### Schema

**`Schema(name: str, description: str)`**

- Creates a configuration schema with a name and description

**`schema.add(item: Schema | Group | Field) -> Self`**

- Adds a field, nested schema, or group constraint
- Returns self for method chaining

**`schema.validate(data: dict)`**

- Validates data against the schema
- Raises `ValueError` on validation failure

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
