# Project NetMagic Base Session Module

# Python Modules
from ipaddress import (
    IPv4Address as IPv4,
    IPv6Address as IPv6,
)

# Third-Party Modules
from netmiko import BaseConnection

# Local Modules
from netmagic.common.types import Transport

class Session:
    """
    Base class for configuration or interaction session
    """
    def __init__(self, host: str|IPv4|IPv6, username: str, password: str,
                 port: int|str = 22, connection: BaseConnection = None,
                 transport: Transport = Transport.SSH, *args, **kwargs) -> None:
        self.connection = connection
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.transport = transport

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        self.connection = None


# PLANNED SPLIT-OUT
class NETCONFSession(Session):
    """
    Container for NETCONF Session via `ncclient`
    """
    def __init__(self) -> None:
        super().__init__()

    def connect(self) -> None:
        """"""
        super().connect()

    def disconnect(self) -> None:
        """"""
        super().disconnect()


class RESTCONFSession(Session):
    """
    Container for RESTCONF Session
    """
    def __init__(self) -> None:
        super().__init__()

    def connect(self) -> None:
        """"""
        super().connect()

    def disconnect(self) -> None:
        """"""
        super().disconnect()
