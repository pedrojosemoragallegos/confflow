from pydantic import BaseModel as _BaseModel, Field

from .confflow_manager import ConfflowManager


class BaseConfig(_BaseModel):
    """Base configuration model, extend as necessary."""

    pass


__all__ = ["BaseConfig", "Field", "ConfflowManager"]
