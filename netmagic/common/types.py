from enum import Enum

from typing import (
    TypeAlias, TypeVar, Iterable,
    Dict, Any, TYPE_CHECKING
)

from ipaddress import (
    IPv4Address as IPv4,
    IPv6Address as IPv6,
)

if TYPE_CHECKING:
    from mactools import MacAddress

HostT: TypeAlias = str|IPv4|IPv6
ConfigSet: TypeAlias = Iterable[str]|str
KwDict: TypeAlias = Dict[str, Any]
FSMOutputT: TypeAlias = list[dict[str, str]]
MacT: TypeAlias = MacAddress|str|int

class Transport(Enum):
    SSH = 'ssh'
    SERIAL = 'serial'
    TELNET = 'telnet'
    NETCONF = 'netconf'
    RESTCONF = 'restconf'
    CUSTOM = 'custom'