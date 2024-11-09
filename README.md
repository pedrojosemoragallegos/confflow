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

### 1. Define Your Configuration Models

Define configuration schemas using Pydantic:

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal

class CommonSettings(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="The name of the configuration.")
    enabled: bool = Field(default=True, description="Indicates if this configuration is enabled.")
    priority: int = Field(default=1, ge=1, le=10, description="Priority level, must be between 1 and 10.")

class DatabaseConfig(BaseModel):
    db_url: str = Field(..., pattern=r"^(postgres|mysql|sqlite)://", description="Database connection URL.")
    max_connections: int = Field(default=10, ge=1, le=100, description="Max number of connections.")
    timeout: Optional[int] = Field(default=30, ge=10, le=300, description="Timeout in seconds.")

class APIConfig(BaseModel):
    endpoint: str = Field(..., pattern=r"^https?://", description="API endpoint URL.")
    auth_token: Optional[str] = Field(None, description="Optional authentication token.")
    retries: int = Field(default=3, ge=0, le=10, description="Number of retries in case of failure.")

class FeatureFlags(BaseModel):
    experimental_feature: bool = Field(default=False, description="Toggle for experimental feature.")
    legacy_mode: bool = Field(default=False, description="Enable legacy mode for backward compatibility.")

# Mutually Exclusive Models
class FileStorageConfig(BaseModel):
    storage_path: str = Field(..., description="Path to the storage directory.")
    max_size_mb: int = Field(default=100, ge=10, le=1024, description="Maximum storage size in MB.")
    backup_enabled: bool = Field(default=True, description="Enable backup for stored files.")

class CloudStorageConfig(BaseModel):
    provider: Literal['aws', 'gcp', 'azure'] = Field(..., description="Cloud storage provider.")
    bucket_name: str = Field(..., min_length=3, description="Name of the cloud storage bucket.")
    region: Optional[str] = Field(None, description="Optional region of the cloud storage bucket.")
```

### 2. Register Schemas and Define Mutually Exclusive Groups

```python
from confflow import ConfflowManager

# Initialize and register schemas
confflow_manager = ConfflowManager()
confflow_manager.register_schemas(CommonSettings, FeatureFlags, CloudStorageConfig, DatabaseConfig)

# Set mutually exclusive groups
confflow_manager.set_mutual_exclusive_groups([CloudStorageConfig, DatabaseConfig])
```

### 3. Generate a YAML Template

```python
confflow_manager.create_template('template_config.yaml')
```

This will generate a configuration template like:

```yaml
CommonSettings:
  name:  # Type: string  Description: The name of the configuration.  
  enabled: True # Type: boolean  Description: Indicates if this configuration is enabled.  
  priority: 1 # Type: integer  Description: Priority level, must be between 1 and 10.  

FeatureFlags:
  experimental_feature:  # Type: boolean  Description: Toggle for experimental feature.  
  legacy_mode:  # Type: boolean  Description: Enable legacy mode for backward compatibility.  

# -------------------------------------
# Mutual exclusive group: Pick only one
# -------------------------------------
CloudStorageConfig:
  provider:  # Type: string ['aws', 'gcp', 'azure']  Description: Cloud storage provider.  
  bucket_name:  # Type: string  Description: Name of the cloud storage bucket.  
  region:  # Types: ['string', 'null']  Description: Optional region of the cloud storage bucket.  

DatabaseConfig:
  db_url:  # Type: string  Description: Database connection URL.  
  max_connections: 10 # Type: integer  Description: Max number of connections.  
  timeout: 30 # Types: ['integer', 'null']  Description: Timeout in seconds.  
# -------------------------------------
```

### 4. Load and Access Configurations

Once the configuration file is populated, load and access the data:

```python
confflow_manager.load_yaml('filled_config.yaml')

# Access specific configurations
common_settings = confflow_manager["CommonSettings"]
print(f"Configuration Name: {common_settings.name}")
print(f"Priority: {common_settings.priority}")

database_config = confflow_manager["DatabaseConfig"]
print(f"Database URL: {database_config.db_url}")
```

### 5. Save Configurations

Save the current configurations back to a YAML file:

```python
confflow_manager.save_config('output_config.yaml')
```

## Development

### Requirements

- Python 3.10+
- Poetry

### Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/pedrojosemoragallegos/confflow.git
cd confflow
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
