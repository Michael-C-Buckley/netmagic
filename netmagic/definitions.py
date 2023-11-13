# Python Modules
from ipaddress import (
    IPv4Address as IPv4,
    IPv6Address as IPv6
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netmagic.handlers.sessions import (
        Session,
        SSHSession,
        NETCONFSession,
        RESTCONFSession
    )

HostType = str|IPv4|IPv6