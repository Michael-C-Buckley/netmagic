# Project NetMagic Switch Library

# Python Modules
from ipaddress import IPv4Address as IPv4
from re import search

# Third-Party Modules
from mactools import MacAddress

# Local Modules
from netmagic.devices import NetworkDevice
from netmagic.sessions.session import Session

class Switch(NetworkDevice):
    """
    Generic switch base class
    """
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.mac: MacAddress = None # GET CHASSIS/MANAGEMENT MAC

    def not_implemented_error_generic(self):
        super().not_implemented_error_generic('switch')
    
    # IDENTITY AND STATUS

    