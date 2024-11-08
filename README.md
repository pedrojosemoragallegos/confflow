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

Here’s an updated guide tailored specifically to the content and functionality demonstrated in your notebook:

---

## Getting Started with Confflow

### 1. **Define Configuration Schemas**

Configuration schemas are defined using `Config` from `confflow`, with field-level validations provided by `Pydantic`.

```python
from pydantic import Field
from confflow import Config

class UserProfile(Config):
    username: str = Field(..., max_length=15, description="Unique username for the user")
    full_name: str = Field(..., description="Full legal name of the user")
    age: int = Field(..., ge=18, le=100, description="Age of the user, must be between 18 and 100")
    email: str = Field(..., pattern=r'^\S+@\S+\.\S+$', description="User's email address")
    phone_number: str = Field(..., pattern=r'^\+\d{1,3}-\d{3}-\d{7,10}$', description="User's contact phone number")
```

Define more schemas similarly:

```python
class AdminSettings(Config):
    admin_id: str = Field(..., description="Unique identifier for the admin")
    permissions: list[str] = Field(..., description="List of permissions assigned to the admin")
    active: bool = Field(True, description="Account active status")
```

---

### 2. **Register Mutually Exclusive Groups**

To ensure certain configurations don’t coexist, use `set_mutual_exclusive_groups` as shown in the notebook:

```python
from confflow import ConfflowManager

confflow_manager = ConfflowManager()

# Define mutual exclusivity between schemas
confflow_manager.set_mutual_exclusive_groups(
    [
        ["AdminSettings", "ModeratorSettings"],
        ["UserProfile", "GuestProfile"]
    ]
)
```

---

### 3. **Generate a Configuration Template**

You can create a YAML template file to guide users on how to structure their configurations.

```python
from pathlib import Path

# Save template to 'template_config.yaml'
confflow_manager.create_template(output_path=Path('template_config.yaml'))
```

Below is an example of a configuration template that Confflow generates when you use the `create_template` method, it will include placeholders for all configuration fields, enforcing mutual exclusivity between specific configuration sets.

```yaml
# ================================================================================
#                                   Configuration Template                        
# ================================================================================
# 
# Purpose:
#   - Use this template to set up configuration values for your environment.
#
# Instructions:
#   - Fill in each field with appropriate values.
#   - Refer to the documentation for detailed descriptions of each field.
#
# Notes:
#   - Only one configuration per mutually exclusive group can be active at a time.
#   - Ensure data types match the specified type for each field.
#
# ================================================================================

# -------------------------------------
# Mutual exclusive group: Pick only one
# -------------------------------------
UserProfile:
  username:            # Type: string (maxLength=15)    Description: Unique username for the user
  full_name:           # Type: string                   Description: Full legal name of the user
  age:                 # Type: integer (minimum=18, maximum=100)  Description: Age of the user, must be between 18 and 100
  email:               # Type: string (pattern='^\S+@\S+\.\S+$')  Description: User's email address
  phone_number:        # Type: string (pattern='^\+\d{1,3}-\d{3}-\d{7,10}$')  Description: User's contact phone number

GuestProfile:
  guest_id:            # Type: string                   Description: Unique identifier for the guest user
  visit_purpose:       # Type: string                   Description: Purpose of the guest's visit
  email:               # Type: string (pattern='^\S+@\S+\.\S+$')  Description: Guest's email address
  access_duration:     # Type: integer                  Description: Allowed access duration in hours

# -------------------------------------

# -------------------------------------
# Mutual exclusive group: Pick only one
# -------------------------------------
AdminSettings:
  admin_id:            # Type: string                   Description: Unique identifier for the admin
  permissions:         # Type: array of strings         Description: List of permissions assigned to the admin
  active: true         # Type: boolean                  Description: Status of the admin account, active or inactive
  email:               # Type: string (pattern='^\S+@\S+\.\S+$')  Description: Admin's email address
  contact_number:      # Type: string (pattern='^\+\d{1,3}-\d{3}-\d{7,10}$')  Description: Admin's contact number

ModeratorSettings:
  mod_id:              # Type: string                   Description: Unique identifier for the moderator
  moderation_areas:    # Type: array of strings         Description: Areas or topics the moderator oversees
  is_active: true      # Type: boolean                  Description: Status of the moderator account
  email:               # Type: string (pattern='^\S+@\S+\.\S+$')  Description: Moderator's email address
  contact_number:      # Type: string (pattern='^\+\d{1,3}-\d{3}-\d{7,10}$')  Description: Moderator's contact number

# -------------------------------------
```

---

### 4. **Load and Use Configurations**

At runtime, load configurations as needed:

```python
from confflow import config_manager

# Load configurations from a predefined source
config_manager.load_config('path_to_config.yaml')

# Access specific configurations
user_profile = config_manager["UserProfile"]
print(user_profile.username)
```

---

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please submit issues and pull requests via the GitHub repository.

## Support

For questions or issues, contact [developmentbypedrojose@gmail.com](mailto:developmentbypedrojose@gmail.com).
