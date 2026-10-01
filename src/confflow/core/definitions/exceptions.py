from __future__ import annotations


class DefinitionError(Exception):
    """Base exception for definition-related errors."""


class ValidationError(DefinitionError):
    """Raised when a value does not satisfy a definition."""
