# Project NetMagic Networking Device Library

from mactools import MacAddress

from netmagic.handlers.sessions import CommandResponse, Session
from netmagic.devices import Device

class NetworkDevice(Device):
    """
    Base class extending `Device` adding common methods and functionality on
    networking equipment, such as switches and routers that servers do not have.
    """
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.mac: MacAddress = None # GET CHASSIS/MANAGEMENT MAC

    def not_implemeneted_error_generic(self):
        """
        Error for methods not available on generic network devices
        """
        raise NotImplementedError('Not available for generic network devices')
    
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
    
    # IDENTITY AND STATUS

    def get_running_config(self) -> CommandResponse:
        """
        Returns the running configuration.
        """
        return self.command('show run')
    
    def get_interface_status(self, interface: str = None) -> CommandResponse:
        """
        Returns interface status of one or all switchports.
        """
        string = 'show interface status'
        if interface:
            string = f'{string} {interface}'
        return self.command(string)

    def get_optics(self) -> CommandResponse:
        """
        Returns information about optical transceivers.
        """
        
    def get_lldp(self) -> CommandResponse:
        """
        Returns LLDP neighbor details information.
        """
        return self.command('show lldp neighbor detail')