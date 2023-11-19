# Project NetMagic Universal Device Library

# Python Modules

# Third-Party Modules
from mactools import MacAddress

# Local Modules
from netmagic.sessions import TerminalSession

class Device:
    """
    Base class for automation and programmability
    """
    def __init__(self, session: TerminalSession = None) -> None:
        self.mac: MacAddress = None
        self.hostname = None
        self.cli_session: TerminalSession = session

    def connect(self, *args, **kwargs) -> None:
        """
        Pass-through wrapper for CLI connect
        """
        self.cli_session.connect()

    def disconnect(self, *args, **kwargs) -> None:
        """
        Pass-through wrapper for CLI disconnect
        """
        self.cli_session.disconnect()
        
    # COMMANDS

    def command(self, *args, **kwargs):
        """
        Pass-through for terminal commands to the terminal session
        """
        return self.cli_session.command(*args, **kwargs)