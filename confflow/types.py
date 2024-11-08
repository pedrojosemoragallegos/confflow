from functools import wraps
from inspect import signature
from pathlib import Path
from typing import Any, Dict, Union

NestedDict = Dict[str, Union[Any, "NestedDict"]]


def ensure_path(func):
    """Decorator to ensure all parameters with type Union[str, Path] are converted to Path."""
    sig = signature(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Iterate through parameters and convert str to Path where applicable
        for name, value in bound_args.arguments.items():
            param = sig.parameters[name]

            # Check if the parameter has a type hint of Union[str, Path]
            if param.annotation == Union[str, Path] and isinstance(value, str):
                bound_args.arguments[name] = Path(value)

        return func(*bound_args.args, **bound_args.kwargs)

    return wrapper
