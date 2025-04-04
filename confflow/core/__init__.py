from pydantic import BaseModel as _BaseModel, Field

from .config_manager import ConfigManager


class BaseConfig(_BaseModel):
    """Base configuration model, extend as necessary."""

    pass


__all__ = ["BaseConfig", "Field", "ConfigManager"]
