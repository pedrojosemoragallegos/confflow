# Confflow

![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green)

**Confflow** is a lightweight, zero-dependency configuration management library for Python applications. It provides an intuitive API for defining, validating, and managing configuration schemas with built-in support for mutually exclusive groups and automatic YAML template generation.

## Why Confflow?

- **Zero Dependencies**: No external dependencies beyond Python's standard library
- **Type Safety**: Built-in validation with clear error messages
- **Flexible Architecture**: Support for nested schemas and mutually exclusive configuration groups
- **Auto-Generated Templates**: Create YAML configuration templates with detailed descriptions
- **Clean API**: Intuitive schema definition using method chaining
- **Production Ready**: Comprehensive validation and error handling

## Key Features

### Schema Definition with Method Chaining

```python
from confflow import Manager, Schema, StringField, IntegerField, BooleanField

config_manager = Manager(
    Schema("app", description="Application settings")
    .add(StringField("name", description="App name", default_value="my-app"))
    .add(IntegerField("port", description="Port number", default_value=8080, ge=1024, le=65535))
    .add(BooleanField("debug", description="Debug mode", default_value=False))
)
```

### Mutually Exclusive Configuration Groups

```python
from confflow import MutualExclusive

config_manager = Manager(
    # Choose exactly one database backend
    MutualExclusive(
        Schema("database_postgres", description="PostgreSQL configuration")
        .add(StringField("host", default_value="localhost"))
        .add(IntegerField("port", default_value=5432)),
        
        Schema("database_mysql", description="MySQL configuration")
        .add(StringField("host", default_value="localhost"))
        .add(IntegerField("port", default_value=3306))
    )
)
```

### Rich Field Types with Validation

```python
from confflow import StringField, IntegerField, FloatField, BooleanField, StringListField, DateField
from datetime import datetime

Schema("advanced", description="Advanced configuration options")
.add(StringField("email", regex=r"^[^@]+@[^@]+\.[^@]+$"))
.add(StringField("log_level", enum=["DEBUG", "INFO", "WARN", "ERROR"]))
.add(StringListField("allowed_ips", min_items=1, unique_items=True))
.add(FloatField("timeout", ge=0.1, le=300.0))
.add(DateField("start_date", default_value=datetime.now()))
```

## Installation

### Using pip (Recommended)

```bash
pip install confflow
```

### From Source

```bash
git clone https://github.com/pedrojosemoragallegos/confflow.git
cd confflow
pip install .
```

## Quick Start

### 1. Define Your Configuration Schema

```python
from confflow import Manager, Schema, StringField, IntegerField, BooleanField, MutualExclusive

config_manager = Manager(
    # Core application settings
    Schema("app", description="Core application configuration")
    .add(StringField("name", description="Application name", 
                     default_value="my-service", min_length=3, max_length=50))
    .add(StringField("version", description="Application version", 
                     default_value="1.0.0", regex=r"^\d+\.\d+\.\d+$"))
    .add(IntegerField("port", description="HTTP port", 
                      default_value=8080, ge=1024, le=65535)),
    
    # Environment-specific configuration (choose one)
    MutualExclusive(
        Schema("development", description="Development environment")
        .add(BooleanField("debug", description="Enable debug logging", default_value=True))
        .add(StringField("log_level", description="Logging level", 
                        default_value="DEBUG", enum=["DEBUG", "INFO", "WARN", "ERROR"])),
        
        Schema("production", description="Production environment")
        .add(BooleanField("debug", description="Enable debug logging", default_value=False))
        .add(StringField("log_level", description="Logging level", 
                        default_value="ERROR", enum=["DEBUG", "INFO", "WARN", "ERROR"]))
        .add(StringField("secret_key", description="Production secret key", min_length=32))
    ),
    
    # Feature toggles
    Schema("features", description="Feature flags and toggles")
    .add(BooleanField("enable_auth", description="Enable authentication", default_value=True))
    .add(BooleanField("enable_cache", description="Enable caching", default_value=False))
)
```

### 2. Generate Configuration Template

```python
# Generate a YAML template with descriptions
config_manager.template("config_template.yaml", descriptions=True)
```

This creates a comprehensive template with detailed validation information:

```yaml
# Core application configuration
app:
  # Application name
  # type: string
  # constraints:
  #   - MinLength('Value must be at least 3 characters long')
  #   - MaxLength('Value must be at most 50 characters long')
  name: my-service
  # Application version
  # type: string
  # constraints:
  #   - Regex('Value must match pattern ^\d+\.\d+\.\d+$')
  version: 1.0.0
  # HTTP port
  # type: integer
  # constraints:
  #   - GreaterThanOrEqual('Value must be >= 1024')
  #   - LessThanOrEqual('Value must be <= 65535')
  port: 8080

# ╔══════════════════════════════════════════════════════════════╗
# ║ MUTUALLY EXCLUSIVE: Choose ONE of the following 2 options  ║
# ╚══════════════════════════════════════════════════════════════╝

# Development environment
development:
  # Enable debug logging
  # type: boolean
  debug: true
  # Logging level
  # type: string
  # constraints:
  #   - EnumValues("Value must be one of ['DEBUG', 'INFO', 'WARN', 'ERROR']")
  log_level: DEBUG

# ┌─── OR ───┐

# Production environment
production:
  # Enable debug logging  
  # type: boolean
  debug: false
  # Logging level
  # type: string
  # constraints:
  #   - EnumValues("Value must be one of ['DEBUG', 'INFO', 'WARN', 'ERROR']")
  log_level: ERROR
  # Production secret key
  # type: string
  # constraints:
  #   - MinLength('Value must be at least 32 characters long')
  secret_key:

# Feature flags and toggles
features:
  # Enable authentication
  # type: boolean
  enable_auth: true
  # Enable caching
  # type: boolean
  enable_cache: false
```

### 3. Load and Use Configuration

```python
# Load configuration from YAML file
config = config_manager.load("my_config.yaml")

# Access configuration values with type safety
app_name = config["app"]["name"]                    # str
port = config["app"]["port"]                        # int
debug_enabled = config["development"]["debug"]      # bool (if development was chosen)
auth_enabled = config["features"]["enable_auth"]   # bool

print(f"Starting {app_name} on port {port}")
if debug_enabled:
    print("Debug mode is enabled")
```

## Advanced Usage

### Nested Schemas

```python
Schema("database", description="Database configuration")
.add(
    Schema("connection", description="Connection settings")
    .add(StringField("host", default_value="localhost"))
    .add(IntegerField("port", default_value=5432))
    .add(
        Schema("credentials", description="Authentication")
        .add(StringField("username", default_value="user"))
        .add(StringField("password_env", description="Environment variable for password"))
    )
)
```

### Complex Validation

```python
from confflow import StringListField, FloatField
from datetime import datetime

Schema("monitoring", description="Monitoring and alerting")
.add(StringListField("alert_emails", description="Email addresses for alerts",
                     min_items=1, max_items=10, regex=r"^[^@]+@[^@]+\.[^@]+$"))
.add(FloatField("cpu_threshold", description="CPU alert threshold (0-100)",
                ge=0.0, le=100.0, default_value=80.0))
.add(DateField("maintenance_start", description="Maintenance window start",
               default_value=datetime(2024, 1, 1, 2, 0)))
```

### Environment-based Configuration

```python
# Define environment-specific schemas
MutualExclusive(
    Schema("local", description="Local development")
    .add(StringField("db_file", default_value="./local.db")),
    
    Schema("staging", description="Staging environment")
    .add(StringField("db_host", default_value="staging-db.internal"))
    .add(BooleanField("mock_external_apis", default_value=True)),
    
    Schema("production", description="Production environment")
    .add(StringField("db_host", default_value="prod-db.internal"))
    .add(StringField("monitoring_endpoint"))
    .add(BooleanField("strict_mode", default_value=True))
)
```

## Field Types and Validation

| Field Type        | Description          | Validation Options                                          |
| ----------------- | -------------------- | ----------------------------------------------------------- |
| `StringField`     | Text values          | `min_length`, `max_length`, `regex`, `enum`                 |
| `IntegerField`    | Whole numbers        | `ge` (≥), `le` (≤), `gt` (>), `lt` (<)                      |
| `FloatField`      | Decimal numbers      | `ge`, `le`, `gt`, `lt`                                      |
| `BooleanField`    | True/false values    | None                                                        |
| `StringListField` | List of strings      | `min_items`, `max_items`, `unique_items`, string validation |
| `DateField`       | Date/datetime values | None                                                        |

### Built-in Constraint System

Confflow uses a robust constraint system with descriptive error messages. Each constraint generates clear validation feedback:

```python
# String constraints
StringField("username", min_length=3, max_length=20)
# Generates: MinLength('Value must be at least 3 characters long')
#           MaxLength('Value must be at most 20 characters long')

StringField("email", regex=r"^[^@]+@[^@]+\.[^@]+$")  
# Generates: Regex('Value must match pattern ^[^@]+@[^@]+\\.[^@]+$')

StringField("status", enum=["active", "inactive", "pending"])
# Generates: EnumValues("Value must be one of ['active', 'inactive', 'pending']")

# Numeric constraints  
IntegerField("port", ge=1024, le=65535)
# Generates: GreaterThanOrEqual('Value must be >= 1024')
#           LessThanOrEqual('Value must be <= 65535')

FloatField("cpu_threshold", gt=0.0, lt=100.0)
# Generates: GreaterThan('Value must be greater than 0.0')
#           LessThan('Value must be less than 100.0')
```

### Validation Examples

```python
# Email validation with detailed constraints
StringField("email", 
           description="User email address",
           regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
           min_length=5, max_length=100)

# Port number with range validation
IntegerField("port", 
            description="HTTP server port",
            ge=1024, le=65535, default_value=8080)

# Enum field with restricted values
StringField("log_level", 
           description="Application logging level",
           enum=["DEBUG", "INFO", "WARN", "ERROR"], 
           default_value="INFO")

# List field with item constraints
StringListField("allowed_origins", 
               description="CORS allowed origins",
               min_items=1, max_items=10, unique_items=True,
               regex=r"^https?://[a-zA-Z0-9.-]+$")
```

## Best Practices

### 1. Use Descriptive Names and Documentation

```python
Schema("cache", description="Redis caching configuration for session storage and API responses")
.add(StringField("redis_url", description="Redis connection URL (redis://host:port/db)"))
.add(IntegerField("ttl_seconds", description="Default TTL for cached items in seconds",
                  default_value=3600, ge=60, le=86400))
```

### 2. Leverage Mutually Exclusive Groups

```python
# Good: Clear separation of deployment targets
MutualExclusive(
    Schema("aws_deployment", description="AWS ECS deployment"),
    Schema("kubernetes_deployment", description="Kubernetes deployment"),
    Schema("docker_deployment", description="Standalone Docker deployment")
)
```

### 3. Provide Sensible Defaults

```python
# Good: Reasonable defaults for common use cases
Schema("http", description="HTTP server configuration")
.add(IntegerField("port", default_value=8080, ge=1024, le=65535))
.add(IntegerField("timeout_seconds", default_value=30, ge=1, le=300))
.add(BooleanField("enable_compression", default_value=True))
```

### 4. Create Custom Field Types for Reusability

Confflow allows you to create custom field types that encapsulate common validation patterns, making your schemas more maintainable and expressive:

```python
from confflow import Field, Constraint
from confflow.constraints import Regex, GreaterThanOrEqual, LessThanOrEqual
from typing import Optional, Literal

class IPAddressField(Field[str]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[str] = None,
        version: Optional[Literal[4, 6]] = None,
    ):
        constraints: list[Constraint[str]] = []
        
        if version == 4:
            ipv4_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
            constraints.append(Regex(ipv4_pattern))
        elif version == 6:
            ipv6_pattern = r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$"
            constraints.append(Regex(ipv6_pattern))
        else:
            # Accept both IPv4 and IPv6
            ip_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$"
            constraints.append(Regex(ip_pattern))
        
        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )

class PortField(Field[int]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[int] = None,
        range_type: Optional[Literal["well_known", "registered", "dynamic"]] = None,
    ):
        constraints: list[Constraint[int]] = []
        
        if range_type == "well_known":
            constraints.extend([GreaterThanOrEqual(0), LessThanOrEqual(1023)])
        elif range_type == "registered":
            constraints.extend([GreaterThanOrEqual(1024), LessThanOrEqual(49151)])
        elif range_type == "dynamic":
            constraints.extend([GreaterThanOrEqual(49152), LessThanOrEqual(65535)])
        else:
            constraints.extend([GreaterThanOrEqual(0), LessThanOrEqual(65535)])
        
        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )

class URLField(Field[str]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[str] = None,
        schemes: Optional[list[Literal["http", "https", "ftp", "ftps", "ws", "wss"]]] = None,
        max_length: Optional[int] = None,
    ):
        constraints: list[Constraint[str]] = []
        
        if schemes:
            scheme_pattern = "|".join(schemes)
            url_pattern = rf"^(?:{scheme_pattern})://[^\s/$.?#].[^\s]*$"
        else:
            url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        
        constraints.append(Regex(url_pattern))
        
        if max_length:
            constraints.append(MaxLength(max_length))
        
        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )

# Usage in schemas
config_manager = Manager(
    Schema("network", description="Network configuration")
    .add(IPAddressField("bind_address", description="Server bind address", 
                        version=4, default_value="127.0.0.1"))
    .add(PortField("http_port", description="HTTP server port", 
                   range_type="registered", default_value=8080))
    .add(URLField("api_endpoint", description="External API endpoint",
                  schemes=["https"], max_length=200)),
    
    Schema("firewall", description="Firewall configuration")
    .add(StringListField("allowed_ips", description="Allowed IP addresses",
                         # Use IPAddressField validation logic here
                         regex=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"))
)
```

**Benefits of custom fields:**

- **Reusability**: Define validation logic once, use everywhere
- **Domain-specific**: Create fields that match your application's domain (e.g., `EmailField`, `PhoneField`, `CurrencyField`)
- **Encapsulation**: Keep complex validation logic contained within field definitions
- **Consistency**: Ensure the same validation rules across your entire configuration schema
- **Documentation**: Custom fields serve as self-documenting domain concepts

### 5. Use Validation Appropriately

```python
# Good: Validate critical configuration
StringField("database_url", 
           description="Database connection string",
           regex=r"^(postgresql|mysql|sqlite)://.*",
           min_length=10)

IntegerField("max_connections", 
            description="Maximum database connections",
            ge=1, le=1000, default_value=20)
```

## Error Handling

Confflow provides clear error messages for validation failures:

```python
try:
    config = config_manager.load("invalid_config.yaml")
except ValidationError as e:
    print(f"Configuration validation failed: {e}")
    # Handle the error appropriately
```

## Development

### Requirements

- Python 3.10–3.13
- No external dependencies

### Setup

```bash
git clone https://github.com/pedrojosemoragallegos/confflow.git
cd confflow
pip install -e .
```

### Testing

```bash
python -m pytest tests/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

**Pedro José Mora Gallegos**  

- LinkedIn: [pedro-jose-mora-gallegos](https://www.linkedin.com/in/pedro-jose-mora-gallegos)
- GitHub: [pedrojosemoragallegos](https://github.com/pedrojosemoragallegos)

---

**Why choose Confflow?** In a world of complex configuration management tools with heavy dependencies, Confflow offers a refreshing approach: powerful features with zero external dependencies, making it perfect for projects that value simplicity and reliability.
