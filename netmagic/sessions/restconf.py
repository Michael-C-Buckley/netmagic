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
        """"""
        super().connect()

    def disconnect(self) -> None:
        """"""
        super().disconnect()
