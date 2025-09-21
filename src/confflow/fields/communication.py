from __future__ import annotations

import typing

from confflow.constraints import Constraint, MaxLength, Regex
from confflow.schema.field import Field


class EmailField(Field[str]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: str | None = None,
        max_length: int | None = None,
        domains: list[str] | None = None,
    ) -> None:
        constraints: list[Constraint[str]] = []

        email_pattern: str
        if domains:
            domain_pattern: str = "|".join(
                [domain.replace(".", r"\.") for domain in domains],
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
        default_value: str | None = None,
        format_type: typing.Literal["international", "us", "digits_only"] | None = None,
        country_code: str | None = None,
    ) -> None:
        constraints: list[Constraint[str]] = []

        phone_pattern: str
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
            phone_pattern = r"^(?:\+[1-9]\d{0,3}[-.\s]?)?\(?([0-9]{1,4})\)?[-.\s]?([0-9]{1,4})[-.\s]?([0-9]{1,9})$"  # noqa: E501

        constraints.append(Regex(phone_pattern))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )
