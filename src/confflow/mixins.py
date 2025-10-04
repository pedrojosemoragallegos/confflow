from abc import ABC, abstractmethod


class FormattedStringMixin(ABC):
    @abstractmethod
    def to_formatted_string(self, indent: int = 0) -> str: ...
