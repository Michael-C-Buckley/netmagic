# NetMagic NETCONF Session

# Local Modules
from netmagic.sessions.session import Session


class NETCONFSession(Session):
    """
    Container for NETCONF Session via `ncclient`
    """

    def __init__(self) -> None:
        raise NotImplementedError("Feature is not yet implemented.")
        # super().__init__()

    def connect(self) -> None:
        """"""
        super().connect()

    def disconnect(self) -> None:
        """"""
        super().disconnect()
