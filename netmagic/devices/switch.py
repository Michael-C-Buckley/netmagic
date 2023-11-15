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

    def not_implemeneted_error_generic(self):
        """
        Error for methods not available on generic switches
        """
        raise NotImplementedError('Not available for generic switches')
    
    # IDENTITY AND STATUS

    