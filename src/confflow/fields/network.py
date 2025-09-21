from __future__ import annotations

import typing

from confflow.constraints import (
    Constraint,
    GreaterThanOrEqual,
    LessThanOrEqual,
    MaxLength,
    Regex,
)
from confflow.schema.field import Field


class IPAddressField(Field[str]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: str | None = None,
        version: typing.Literal[4, 6] | None = None,
    ) -> None:
        constraints: list[Constraint[str]] = []

        if version == 4:
            ipv4_pattern: str = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"  # noqa: E501
            constraints.append(Regex(ipv4_pattern))
        elif version == 6:
            ipv6_pattern: str = r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$"
            constraints.append(Regex(ipv6_pattern))
        else:
            ip_pattern: str = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$"  # noqa: E501
            constraints.append(Regex(ip_pattern))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class MACAddressField(Field[str]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: str | None = None,
        separator: typing.Literal[":", "-"] | None = None,
    ) -> None:
        constraints: list[Constraint[str]] = []

        mac_pattern: str
        if separator == ":":
            mac_pattern = r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
        elif separator == "-":
            mac_pattern = r"^([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$"
        else:
            mac_pattern = r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$"

        constraints.append(Regex(mac_pattern))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class PortField(Field[int]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: int | None = None,
        range_type: typing.Literal["well_known", "registered", "dynamic"] | None = None,
    ) -> None:
        constraints: list[Constraint[int]] = []

        if range_type == "well_known":
            constraints.extend([GreaterThanOrEqual(0), LessThanOrEqual(1023)])
        elif range_type == "registered":
            constraints.extend([GreaterThanOrEqual(1024), LessThanOrEqual(49151)])
        elif range_type == "dynamic":
            constraints.extend([GreaterThanOrEqual(49152), LessThanOrEqual(65535)])
        else:
            constraints.extend([GreaterThanOrEqual(0), LessThanOrEqual(65535)])

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class URLField(Field[str]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: str | None = None,
        schemes: list[typing.Literal["http", "https", "ftp", "ftps", "ws", "wss"]]
        | None = None,
        max_length: int | None = None,
    ) -> None:
        constraints: list[Constraint[str]] = []

        url_pattern: str
        if schemes:
            scheme_pattern: str = "|".join(schemes)
            url_pattern = rf"^(?:{scheme_pattern})://[^\s/$.?#].[^\s]*$"
        else:
            url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"

        constraints.append(Regex(url_pattern))

        if max_length:
            constraints.append(MaxLength(max_length))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class HostnameField(Field[str]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: str | None = None,
        fqdn_only: bool = False,
        max_length: int | None = None,
    ) -> None:
        constraints: list[Constraint[str]] = []

        hostname_pattern: str
        if fqdn_only:
            hostname_pattern = (
                r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
            )
        else:
            hostname_pattern = r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"  # noqa: E501

        constraints.append(Regex(hostname_pattern))

        if max_length:
            constraints.append(MaxLength(max_length))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class CIDRField(Field[str]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: str | None = None,
        version: typing.Literal[4, 6] | None = None,
    ) -> None:
        constraints: list[Constraint[str]] = []

        cidr_pattern: str
        if version == 4:
            cidr_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/(?:[0-9]|[1-2][0-9]|3[0-2])$"  # noqa: E501
        elif version == 6:
            cidr_pattern = r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}/(?:[0-9]|[1-9][0-9]|1[0-1][0-9]|12[0-8])$"  # noqa: E501
        else:
            ipv4_cidr = r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/(?:[0-9]|[1-2][0-9]|3[0-2])"  # noqa: E501
            ipv6_cidr = r"(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}/(?:[0-9]|[1-9][0-9]|1[0-1][0-9]|12[0-8])"  # noqa: E501
            cidr_pattern = f"^(?:{ipv4_cidr}|{ipv6_cidr})$"

        constraints.append(Regex(cidr_pattern))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )
