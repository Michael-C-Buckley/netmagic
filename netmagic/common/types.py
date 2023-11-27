from enum import Enum

from typing import (
    TypeAlias, TypeVar, Iterable,
    Dict, Any
)

from ipaddress import (
    IPv4Address as IPv4,
    IPv6Address as IPv6,
)

HostT: TypeAlias = str|IPv4|IPv6
ConfigSet: TypeAlias = Iterable[str]|str
KwDict: TypeAlias = Dict[str, Any]
FSMOutputT: TypeAlias = list[dict[str, str]]

class Transport(Enum):
    SSH = 'ssh'
    SERIAL = 'serial'
    TELNET = 'telnet'
    NETCONF = 'netconf'
    RESTCONF = 'restconf'
    CUSTOM = 'custom'