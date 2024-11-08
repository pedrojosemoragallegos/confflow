# Configuration Manager Package

## Overview

This package provides a comprehensive framework for managing configuration files in Python projects. It ensures validation, mutual exclusivity, and easy template generation for configurations using `pydantic` models.

## Features

- **Schema Registration**: Register `pydantic` models as configuration schemas.
- **Mutual Exclusivity**: Define groups of mutually exclusive configurations.
- **Template Generation**: Generate a configuration template to guide users.
- **Validation**: Validate configuration data against predefined schemas.
- **Dynamic Updates**: Update configuration values at runtime.
- **Example Config Generator**: Generate example configuration files for reference.

## Installation

```bash
pip install confflow
```

## Getting Started

### 1. Define Configuration Schemas

Use `pydantic.BaseModel` to define your configuration schemas.

```python
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str

class APIConfig(BaseModel):
    endpoint: str
    token: str
```

### 2. Register Schemas

Register your schemas using `register_schema`.

```python
from confflow import register_schema

register_schema(DatabaseConfig)
register_schema(APIConfig)
```

### 3. Define Mutually Exclusive Groups

If you have configurations that cannot coexist, define mutually exclusive groups.

```python
from confflow import register_mutually_exclusive

register_mutually_exclusive(DatabaseConfig, APIConfig)
```

### 4. Generate a Template

Create a template configuration file to guide users.

```python
from confflow import create_template
from pathlib import Path

create_template(Path("config_template.yaml"))
```

### 5. Load Configuration

Load the configuration file at runtime.

```python
from confflow import config_manager

config_manager.load_config()

db_config = config_manager["DatabaseConfig"]
print(db_config.host)
```

### 6. Update Configuration

Update configuration values dynamically.

```python
db_config.host = "new-host"
db_config.update()
```

## Environment Variables

- `CONFIG_PATH`: Specify the path to the configuration file. If not set, the package defaults to `config.yaml` in the project root.

## Exception Handling

- **FileNotFoundError**: Raised if the configuration file is missing.
- **ValidationError**: Raised if configuration data fails validation.
- **ValueError**: Raised for mutual exclusivity violations or unknown configurations.

## API Reference

### `register_schema(schema: Type[BaseModel])`

Register a configuration schema.

### `register_mutually_exclusive(*schemas: Type[BaseModel])`

Register mutually exclusive configuration schemas.

### `create_template(output_path: Path)`

Generate a template configuration file.

### `get_config_path() -> Path`

Get the path to the configuration file.

### `ConfigManager`

- `load_config()`: Load and validate the configuration file.
- `generate_example_config()`: Generate an example configuration file.
- `__getitem__(name: str) -> ConfigProxy`: Access a specific configuration.

### `ConfigProxy`

- Access configuration attributes.
- Update configuration values dynamically.

## Example Usage

```python
from confflow import config_manager, list_configs

print("Registered Configs:", list_configs())

api_config = config_manager["APIConfig"]
print(api_config.endpoint)

api_config.token = "new-token"
api_config.update()
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please submit issues and pull requests via the GitHub repository.

## Support

For questions or issues, contact [developmentbypedrojose@gmail.com](mailto:developmentbypedrojose@gmail.com).
