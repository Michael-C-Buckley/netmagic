
# Python Modules
from typing import Iterable
from datetime import datetime

# Third-Party Modules
from netmiko import BaseConnection, ReadTimeout

# Local Modules
from netmagic.definitions import HostType, CommandContainer
from netmagic.handlers.connect import netmiko_connect
from netmagic.handlers.response import CommandResponse

# SEE BOTTOM FOR TYPE CONSTANTS
# INCLUDES: AnySession, SessionContainer

class Session:
    """
    Base class for configuration or interaction session
    """
    def __init__(self,
                 connection: BaseConnection,
                 host: HostType,
                 username: str,
                 password: str,
                 port: int = 22,
                 *args, **kwargs
                 ) -> None:
        self.connection = connection
        self.username = username
        self.password = password
        self.host = host
        self.port = port

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        self.connection = None


class SSHSession(Session):
    """
    Container for SSH session
    """
    def __init__(self,
                 connection: BaseConnection,
                 device_type: str,
                 host: HostType,
                 username: str,
                 password: str,
                 secret: str = None,
                 port: int = 22,
                 engine: str = 'netmiko',
                 *args, **kwargs
                 ) -> None:
        super().__init__(connection, host, username, password, port)
        self.secret = secret
        self.engine = engine
        self.device_type = device_type

        # Collect the remaining kwargs and offer them on connection
        self.connection_kwargs = {**kwargs}
        

        self.command_log = []
        self.prompt = None

    # CONNECTION HANDLING

    def connect(self) -> None:
        """
        Connect SSH session using the selected attributes
        """
        attribute_filter = ['host','port','username','password','device_type']
        connection_kwargs = {k:v for k,v in self.__dict__.items() if k in attribute_filter}
        if self.connection_kwargs:
            connection_kwargs.update(self.connection_kwargs)
        self.connection = netmiko_connect(**connection_kwargs)

    def disconnect(self):
        self.connection.disconnect()
        super().disconnect()

    def get_hostname(self) -> str:
        """
        Generic stand-in that returns the prompt for non-specific devices
        """
        return self.prompt
    
    # COMMANDS

    def command_try_loop(self, command_string: str, expect_string: str = None,
                         read_timeout: float = 10.0, *args, **kwargs) -> str|Exception:
        """
        """
        command_kwargs = {k:v for k,v in locals().items() if k not in ['args', 'kwargs', 'self']}
        command_kwargs = {**kwargs, **command_kwargs}
        try:
            return self.connection.send_command(*args, **command_kwargs)
        except ReadTimeout as e:
            return e
        


    def command(self, command: CommandContainer, expect_string: str = None,
                blind: bool = False, *args, **kwargs) -> CommandResponse:
        """
        """
        if not self.connection:
            # Error handling and potential reconnecting
            raise AttributeError('No active session to send commands to')

        output_list = []

        # Enter enable mode if needed

        # Handle blind
        if blind:
            pass

        # Handle a single command first
        sent_time = datetime.now()
        output = self.command_try_loop(command, expect_string, *args, **kwargs)
        received_time = datetime.now()
        response = CommandResponse(command, output, sent_time, received_time, self, expect_string)
        self.command_log.append(response)
        return response

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


AnySession = Session|SSHSession|NETCONFSession|RESTCONFSession
SessionContainer = Iterable[AnySession]|AnySession