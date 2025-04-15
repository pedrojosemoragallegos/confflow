from typing import Callable, Dict, Optional, Type, TypeAlias

from .base_formatter import BaseFormatter

FormatterClass: TypeAlias = Type[BaseFormatter]
FormatterDecorator: TypeAlias = Callable[[FormatterClass], FormatterClass]
FormatterRegistryMap: TypeAlias = Dict[str, FormatterClass]


class FormatterRegistry:
    _registry: FormatterRegistryMap = {}

    @classmethod
    def register(cls, key: str) -> FormatterDecorator:
        def decorator(formatter_cls: FormatterClass) -> FormatterClass:
            if not issubclass(formatter_cls, BaseFormatter):
                raise TypeError(
                    f"Class {formatter_cls.__name__} must inherit from 'BaseFormatter'."
                )

            cls._registry[key] = formatter_cls
            return formatter_cls

        return decorator

    @classmethod
    def get(cls, key: str) -> Optional[FormatterClass]:
        return cls._registry.get(key)

    @classmethod
    def all(cls) -> FormatterRegistryMap:
        return dict(cls._registry)
