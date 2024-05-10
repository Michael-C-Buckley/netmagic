# NetMagic Type Module

# Python Modules
from enum import Enum
from ipaddress import (
    IPv4Address as IPv4,
    IPv6Address as IPv6,
)
from typing import Any, Iterable, TypeAlias

# Third-Part Modules
from mactools import MacAddress


HostT: TypeAlias = str|IPv4|IPv6
ConfigSet: TypeAlias = Iterable[str]|str
KwDict: TypeAlias = dict[str, Any]

FSMOutputT: TypeAlias = list[dict[str, str]]
FSMDataT: TypeAlias = dict[str, Any]

MacT: TypeAlias = MacAddress|str|int


class Transport(Enum):
    SSH = 'ssh'
    SERIAL = 'serial'
    TELNET = 'telnet'
    NETCONF = 'netconf'
    RESTCONF = 'restconf'
    CUSTOM = 'custom'


class Engine(Enum):
    NETMIKO = 'netmiko'
    SCRAPLI = 'scrapli'


class Vendors(Enum):
    BROCADE = 'brocade'
    CISCO = 'cisco'
    RUCKUS = 'ruckus'


class SFPAlert(Enum):
    NORMAL = 'Normal'
    LOW_WARN = 'low warning'
    HIGH_WARN = 'high warning'
    LOW_ALARM = 'low alarm'
    HIGH_ALARM = 'high alarm'


class TDRStatus(Enum):
    NORMAL = ('Normal', 'terminated')
    CROSSTALK = ('Crosstalk', 'crosstalk')
    OPEN = ('Open', 'open')
    SHORT = ('Short', 'short')
    UNKNOWN = ('Unknown', 'unknown')

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
        raise ValueError(f'Value `{value}` not a valid TDRStatus')