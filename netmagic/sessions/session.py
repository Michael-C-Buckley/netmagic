# Project NetMagic Base Session Module

# Third-Party Modules
from netmiko import BaseConnection

# Local Modules
from netmagic.common import Transport, HostT

class Session:
    """
    Base class for configuration or interaction session
    """
    def __init__(self, host: HostT, username: str, password: str,
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
