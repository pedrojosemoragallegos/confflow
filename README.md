# Confflow

![Python](https://img.shields.io/badge/python-^3.10-blue)  
![License](https://img.shields.io/github/license/pedrojosemoragallegos/confflow)

## Overview

**Confflow** is a robust configuration management library designed for Python projects. It provides seamless management of configurations using YAML files and integrates validation via Pydantic models. Confflow ensures that your configurations are logically consistent and simplifies the process of creating, loading, and saving configuration files.

## Features

- **Pydantic Integration**: Validate configurations using Pydantic models.
- **YAML Support**: Load and save configurations in YAML format.
- **Mutually Exclusive Groups**: Enforce logical constraints across configuration options.
- **Singleton Pattern**: Manage configuration instances efficiently.
- **Template Generation**: Automatically generate YAML templates for your configurations.

## Installation

### Clone the Repository

```bash
git clone https://github.com/pedrojosemoragallegos/confflow.git
```

Navigate to the project directory and install the dependencies:

```bash
cd confflow
poetry install
```

## Usage

### 1. Define Your Schemas

Confflow uses Pydantic models to define configuration schemas:

```python
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
```

### 2. Register Schemas

Register your schemas with the `ConfflowManager`:

```python
from confflow import ConfflowManager

manager = ConfflowManager()
manager.register_schemas(DatabaseConfig)
```

### 3. Load Configurations from YAML

Load configurations from a YAML file:

```yaml
DatabaseConfig:
  host: "localhost"
  port: 5432
  username: "admin"
  password: "secret"
```

```python
manager.load_yaml("config.yaml")
db_config = manager["DatabaseConfig"]
print(db_config.host)
```

### 4. Save Configurations

Save your current configurations back to a YAML file:

```python
manager.save_config("output_config.yaml")
```

### 5. Create YAML Templates

Generate a YAML template with instructions:

```python
manager.create_template("template.yaml")
```

## Configuration Groups

Confflow allows you to define mutually exclusive configuration groups:

```python
manager.set_mutual_exclusive_groups([DatabaseConfig, AnotherConfig])
```

This ensures only one configuration in the group can be active at a time.

## Development

### Requirements

- Python 3.10+
- Poetry

### Setup

Clone the repository:

```bash
git clone https://github.com/pedrojosemoragallegos/confflow.git
cd confflow
```

Install dependencies:

```bash
poetry install
```

Run tests:

```bash
poetry run pytest
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Developed by [Pedro José Mora Gallegos](https://www.linkedin.com/in/pedro-jose-mora-gallegos).

## Links

- **Homepage**: [LinkedIn](https://www.linkedin.com/in/pedro-jose-mora-gallegos)  
- **Repository**: [GitHub](https://github.com/pedrojosemoragallegos/confflow)
