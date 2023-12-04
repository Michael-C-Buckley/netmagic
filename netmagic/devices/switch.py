# Project NetMagic Switch Library

# Python Modules
from ipaddress import IPv4Address as IPv4
from re import search

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
        Returns POE status
        """
        show_poe = self.command(poe_command)

        if isinstance(template, str):
            fsm_data = self.fsm_parse(show_poe.response, template)

            host_kwargs = {'host': self.hostname}
            show_poe.fsm_output = {}

            for entry in fsm_data:
                # Host-specific data will show up on only one line
                if (capacity := entry.get('capacity')):
                    host_kwargs['capacity'] = capacity
                if (available := entry.get('available')):
                    host_kwargs['available'] = available

                port = entry.get('port')

                if port:
                    port_kwargs = {k:v for k,v in entry.items() if v}
                    poe_port = POEPort(host = self.hostname, **port_kwargs)
                    show_poe.fsm_output[port] = poe_port

                show_poe.fsm_output[self.hostname] = POEHost(**host_kwargs)

        return show_poe