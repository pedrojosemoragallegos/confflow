from functools import wraps
from typing import Callable, Optional, Type

from pydantic import BaseModel

from .config_manager import config_manager

__all__ = ["config_manager", "register"]


def register(
    description: Optional[str] = None,
    exclusive_group: Optional[str] = None,
) -> Callable[[Type[BaseModel]], Type[BaseModel]]:
    def decorator(cls: Type[BaseModel]) -> Type[BaseModel]:
        @wraps(cls)
        def wrapper(*args, **kwargs):
            return cls(*args, **kwargs)

        config_manager.register_schema(cls, description=description)

        if exclusive_group:
            config_manager._exclusivity_manager.add_to_group(exclusive_group, cls)

        return cls

    return decorator
