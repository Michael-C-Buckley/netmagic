# Project NetMagic Switch Library

# Python Modules
from ipaddress import IPv4Address as IPv4

# Third-Party Modules
from mactools import MacAddress

# Local Modules
from netmagic.common.classes import CommandResponse 
from netmagic.common.classes.status import POEPort, POEHost
from netmagic.devices import NetworkDevice
from netmagic.sessions import Session, TerminalSession

class Switch(NetworkDevice):
    """
    Generic switch base class
    """
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        if isinstance(session, TerminalSession):
            self.session_preparation()
        self.mac: MacAddress = None # GET CHASSIS/MANAGEMENT MAC

    def not_implemented_error_generic(self):
        super().not_implemented_error_generic('switch')
    
    # IDENTITY AND STATUS

    def get_poe_status(self, poe_command: str, template: str|bool) -> CommandResponse:
        """
        Returns POE status by interface name and also the hostname for overall
        capacity and availability data.
        """
        show_poe = self.command(poe_command)

        if isinstance(template, str):
            fsm_data = self.fsm_parse(show_poe.response, template)
            show_poe.fsm_output = {}

            for entry in fsm_data:
                poe_port = POEPort.create(self.hostname, **entry)
                show_poe.fsm_output[entry['port']] = poe_port

            # Add another entry for the chassis using the Filldown values
            poe_host = POEHost.create(self.hostname, **entry)
            show_poe.fsm_output[self.hostname] = poe_host

        return show_poe
    
    def get_interface_vlans(self, template: str|bool = None) -> CommandResponse:
        """
        Returns the VLAN information of the switchports.

        `template` is the path to a custom TextFSM template.  `None` will use the 
        library default version.
        """
        self.not_implemented_error_generic()
