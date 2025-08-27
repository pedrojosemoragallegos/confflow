from typing import Literal, Optional

from ..constraints import (
    Constraint,
    MaxLength,
    Regex,
)
from ..schema.field import Field


class EmailField(Field[str]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[str] = None,
        max_length: Optional[int] = None,
        domains: Optional[list[str]] = None,
    ):
        constraints: list[Constraint[str]] = []

        if domains:
            domain_pattern = "|".join(
                [domain.replace(".", r"\.") for domain in domains]
            )
            email_pattern = rf"^[a-zA-Z0-9._%+-]+@(?:{domain_pattern})$"
        else:
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        constraints.append(Regex(email_pattern))

        if max_length:
            constraints.append(MaxLength(max_length))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class PhoneField(Field[str]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[str] = None,
        format_type: Optional[Literal["international", "us", "digits_only"]] = None,
        country_code: Optional[str] = None,
    ):
        constraints: list[Constraint[str]] = []

        if format_type == "international":
            if country_code:
                phone_pattern = rf"^\+{country_code}[0-9]{{6,14}}$"
            else:
                phone_pattern = r"^\+[1-9]\d{6,14}$"
        elif format_type == "us":
            phone_pattern = (
                r"^(?:\+1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$"
            )
        elif format_type == "digits_only":
            phone_pattern = r"^[0-9]{7,15}$"
        else:
            phone_pattern = r"^(?:\+[1-9]\d{0,3}[-.\s]?)?\(?([0-9]{1,4})\)?[-.\s]?([0-9]{1,4})[-.\s]?([0-9]{1,9})$"

        constraints.append(Regex(phone_pattern))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )
