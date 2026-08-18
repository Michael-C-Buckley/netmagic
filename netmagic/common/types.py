# NetMagic Type Module

# Python Modules
from collections.abc import Iterable
from enum import Enum
from ipaddress import (
    IPv4Address as IPv4,
)
from ipaddress import (
    IPv6Address as IPv6,
)
from typing import Any

# Third-Part Modules
from mactools import MacAddress

type HostT = str | IPv4 | IPv6
type ConfigSet = Iterable[str] | str
type KwDict = dict[str, Any]

type FSMOutputT = list[dict[str, str]]
type FSMDataT = dict[str, Any]

type MacT = MacAddress | str | int


class SwitchportMode(Enum):
    NONE = "none"
    TRUNK = "trunk"
    ACCESS = "access"


class Transport(Enum):
    SSH = "ssh"
    SERIAL = "serial"
    TELNET = "telnet"
    NETCONF = "netconf"
    RESTCONF = "restconf"
    CUSTOM = "custom"


class Engine(Enum):
    NETMIKO = "netmiko"
    SCRAPLI = "scrapli"


class Vendors(Enum):
    BROCADE = "brocade"
    CISCO = "cisco"
    RUCKUS = "ruckus"


class SFPAlert(Enum):
    NONE = "none"
    NORMAL = "normal"
    LOW_WARN = "low warning"
    HIGH_WARN = "high warning"
    LOW_ALARM = "low alarm"
    HIGH_ALARM = "high alarm"


class TDRStatus(Enum):
    NORMAL = ("Normal", "terminated")
    CROSSTALK = ("Crosstalk", "crosstalk")
    OPEN = ("Open", "open")
    SHORT = ("Short", "short")
    UNKNOWN = ("Unknown", "unknown")
    NOT_SUPPORTED = ("Not Supported", "not supported")

    def __new__(cls, *values: object):
        obj = object.__new__(cls)
        obj._value_ = values[0]
        obj.all_values = values
        return obj

    @classmethod
    def create(cls, value):
        for member in cls:
            if value in member.all_values:
                return member
        raise ValueError(f"Value `{value}` not a valid TDRStatus")
