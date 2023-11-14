# Project NetMagic Switch Library

# Python Modules
from ipaddress import IPv4Address as IPv4
from re import search

# Third-Party Modules
from mactools import MacAddress

# Local Modules
from netmagic.devices.universal import Device
from netmagic.handlers.sessions import SessionContainer

class Switch(Device):
    """
    Generic switch base class
    """
    def __init__(self, session: SessionContainer) -> None:
        super().__init__(session)
        self.mac: MacAddress = None # GET CHASSIS/MANAGEMENT MAC

    def not_implemeneted_error_generic(self):
        """
        Error for methods not available on generic switches
        """
        raise NotImplementedError('Not available for generic switches')
    
    # CONFIG HANDLING

    def enable_loop(self, password: str = None) -> bool:
        """
        Inner loop for `enable`
        """

    def enable(self) -> bool:
        """
        Manual SSH enable method useful for proxy SSH
        """

    def config_try_loop(self, config: list[str], exit: bool) -> str:
        """
        Inner loop for `send_config`
        """

    def send_config(self, config: list[str], exit: bool = True,
                    *args, **kwargs) -> str:
        """
        Send config
        """

    def write_memory(self):
        return self.ssh_session.connection.send_command('write memory')
    