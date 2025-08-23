from typing import Optional

from .field import Field


class BooleanField(Field[bool]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[bool] = None,
        required: bool = False,
    ):
        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            constraints=[],
        )
