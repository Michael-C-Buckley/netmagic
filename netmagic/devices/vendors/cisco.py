# NetMagic Cisco Device Library

# Python Modules

# Third-Party Modules

# Local Modules
from netmagic.devices.switch import Switch
from netmagic.handlers import CommandResponse
from netmagic.sessions import Session

class CiscoIOSSwitch(Switch):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    # IDENTITY
    def get_running_config(self) -> CommandResponse:
        """
        Returns the running configuration.
        """
        return super().get_running_config()

    def get_interface_status(self, interface: str = None) -> CommandResponse:
        """
        Returns interface status of one or all switchports.
        """
        return super().get_interface_status(interface)
    
    def get_optics(self) -> CommandResponse:
        """
        Returns information about optical transceivers.
        """
        return super().get_optics()
    
    def get_lldp(self) -> CommandResponse:
        """
        Returns LLDP neighbor details information.
        """
        return super().get_lldp()