# NetMagic Router Library

# Local Modules
from netmagic.devices.network_device import NetworkDevice
from netmagic.sessions import Session

class Router(NetworkDevice):
    """
    Generic router base class
    """
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def not_implemented_error_generic(self):
        super().not_implemented_error_generic('router')