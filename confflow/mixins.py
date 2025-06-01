from typing import Any, Dict, List, Tuple, Type


class PublicReprMixin:
    def __repr__(self) -> str:
        public_attrs: Dict[str, Any] = {
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }

        attrs: str = ", ".join(f"{k}={v!r}" for k, v in public_attrs.items())

        return f"{self.__class__.__name__}({attrs})"


class PropertyReprMixin:
    def __repr__(self) -> str:
        properties: List[Tuple[str, Any]] = []

        cls: Type[Any]

        for cls in self.__class__.__mro__:
            name: str
            attr: Any

            for name, attr in cls.__dict__.items():
                if isinstance(attr, property) and name not in [
                    p[0] for p in properties
                ]:
                    try:
                        value: Any = getattr(self, name)
                        properties.append((name, value))
                    except (AttributeError, Exception):
                        pass

        attrs: str = ", ".join(f"{name}={value!r}" for name, value in properties)

        return f"{self.__class__.__name__}({attrs})"


class ReprMixin:
    def __repr__(self) -> str:
        public_attrs: Dict[str, Any] = {
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }

        properties: Dict[str, Any] = {}

        cls: Type[Any]

        for cls in self.__class__.__mro__:
            name: str
            attr: Any
            for name, attr in cls.__dict__.items():
                if isinstance(attr, property) and name not in properties:
                    try:
                        value: Any = getattr(self, name)
                        properties[name] = value
                    except (AttributeError, Exception):
                        pass

        all_attrs: Dict[str, Any] = {**public_attrs, **properties}

        attrs: str = ", ".join(f"{k}={v!r}" for k, v in all_attrs.items())

        return f"{self.__class__.__name__}({attrs})"
