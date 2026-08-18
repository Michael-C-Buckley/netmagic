# NetMagic RESTCONF Session

# Local Modules
from netmagic.sessions.session import Session


class RESTCONFSession(Session):
    """
    Container for RESTCONF Session
    """

    def __init__(self) -> None:
        raise NotImplementedError("Feature is not yet implemented.")
        # super().__init__()

    def connect(self) -> None:
        """Connect the RESTCONF session."""
        super().connect()

    def disconnect(self) -> None:
        """Disconnect the RESTCONF session."""
        super().disconnect()
