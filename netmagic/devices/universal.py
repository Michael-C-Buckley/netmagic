# Project NetMagic Universal Device Library

# Python Modules

# Third-Party Modules
from mactools import MacAddress

# Local Modules
from netmagic.common.types import FSMOutputT
from netmagic.sessions import TerminalSession
from netmagic.handlers import get_fsm_data

class Device:
    """
    Base class for automation and programmability
    """
    def __init__(self, session: TerminalSession = None) -> None:
        self.mac: MacAddress = None
        self.hostname = None
        self.cli_session: TerminalSession = session
        self.vendor = None

    def not_implemented_error_generic(self, device_type: str = 'device'):
        """
        Error for methods not available on generic device
        """
        raise NotImplementedError(f'Not available for generic {device_type}')

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
    
    # HANDLING

    def fsm_parse(self, input: str|list[str], template: str,
                  split_term: str = None, flatten_key: str = None) -> FSMOutputT:
        """
        Wrapper method for `TextFSM` and `Parse` handler
        """
        return get_fsm_data(input, self.vendor, template, split_term, flatten_key)