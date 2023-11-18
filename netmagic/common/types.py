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