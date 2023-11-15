# Project NetMagic Universal Device Library

# Python Modules

# Third-Party Modules
from mactools import MacAddress

# Local Modules
from netmagic.sessions.session import (
    RESTCONFSession,
    NETCONFSession
)
from netmagic.sessions.session import Session
from netmagic.sessions.terminal import TerminalSession

class Device:
    """
    Base class for automation and programmability
    """
    def __init__(self, session: Session) -> None:
        self.mac: MacAddress = None
        self.hostname = None

        self.cli_session: TerminalSession = None
        self.netconf_session: NETCONFSession = None
        self.restconf_session: RESTCONFSession = None

        def assign_session(session: Session) -> None:
            if isinstance(session, Session):
                session_map = {
                    TerminalSession: 'cli_session',
                    NETCONFSession: 'netconf_session',
                    RESTCONFSession: 'restconf_session',
                }
                if (session_attribute := session_map.get(type(session))):
                    setattr(self, session_attribute, session)
                # LOG UNASSIGNED SESSION

        if isinstance(session, Session):
            assign_session(session)
        elif isinstance(session, list) or isinstance(session, tuple):
            for element in session:
                assign_session(element)
        

    def disconnect_all(self) -> None:
        """
        Closes all open sessions
        """
        for session in [self.cli_session, self.restconf_session, self.netconf_session]:
            if isinstance(session, Session):
                session.disconnect()

    def connect_all(self) -> None:
        """
        Attempts to reconnect non-active sessions
        """
        for session in [self.cli_session, self.restconf_session, self.netconf_session]:
            if isinstance(session, Session):
                if not session.connection:
                    session.connect()

    # COMMANDS

    def command(self, *args, **kwargs):
        """
        Pass-through for terminal commands to the terminal session
        """
        return self.cli_session.command(*args, **kwargs)