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