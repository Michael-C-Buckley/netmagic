# Project NetMagic Networking Device Library

# Python Module
from datetime import datetime
from re import search

# Third-Party Modules
from netmiko import ReadTimeout

# Local Modules
from netmagic.common.classes import CommandResponse, ConfigResponse
from netmagic.common.utils import validate_max_tries
from netmagic.devices import Device
from netmagic.sessions import Session, TerminalSession, RESTCONFSession, NETCONFSession
from netmagic.common import ConfigSet

class NetworkDevice(Device):
    """
    Base class extending `Device` adding common methods and functionality on
    networking equipment, such as switches and routers that servers do not have.
    """
    def __init__(self, session: Session) -> None:
        super().__init__()

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

        if self.cli_session and self.hostname is None:
            self.get_hostname()

    def disconnect(self, session: Session = None) -> None:
        """
        Closes specified session or all sessions
        """
        if session:
            session.disconnect() if isinstance(session, Session) else None
            return
        
        for session in [self.cli_session, self.restconf_session, self.netconf_session]:
            session.disconnect() if isinstance(session, Session) else None
                    
    def connect(self, session: Session = None) -> None:
        """
        Attempts to reconnect non-active sessions
        """
        if session:
            session.connect() if isinstance(session, Session) else None
            return
        
        for session in [self.cli_session, self.restconf_session, self.netconf_session]:
            if isinstance(session, Session):
                if not session.connection:
                    session.connect()

    def not_implemented_error_generic(self, device_type: str = None):
        if device_type is None:
            device_type = 'network device'
        super().not_implemented_error_generic(device_type)
    
    # CONFIG HANDLING

    def enable(self, *args, **kwargs) -> None:
        """
        Manual SSH enable method useful for proxy SSH
        """
        self.not_implemented_error_generic()

    @validate_max_tries
    def send_config(self, config: ConfigSet, max_tries: int = 3, 
                    exit: bool = True, save: bool = True,
                    *args, **kwargs) -> ConfigResponse:
        """
        Send device configuration commands.

        *config: The config to be sent as either a string or iterable of strings
        *max_tries: How many total tries to send if not originally successful
        *exit: bool whether the code should exit global config mode when done
        *save: bool whether the code should save the config after changes
        """
        for i in range(max_tries):

            sent_time = datetime.now()

            try:
                output = self.cli_session.connection.send_config_set(config, exit_config_mode=exit)
            except (ReadTimeout, OSError) as e:
                output = e
            else:
                break

        if save:
            self.write_memory()

        return ConfigResponse(output, config, sent_time, self.cli_session, i+1)

    def write_memory(self):
        """
        Command to save the running configuration
        """
        return self.cli_session.connection.send_command('write memory')
    
    # IDENTITY AND STATUS

    def get_hostname(self) -> CommandResponse:
        hostname = self.command('show run | i hostname')
        if (hostname_match := search(r'hostname\s(.+)', hostname.response)):
            hostname_str = hostname_match.group(1)
        # Check for quotes surrounding the Hostname
        if hostname_str[0] and hostname_str[-1] == '"':
            hostname_str.replace('"','')
        self.hostname = hostname_str
        return hostname

    def get_running_config(self) -> CommandResponse:
        """
        Returns the running configuration.
        """
        return self.command('show run')
    
    def get_interface_status(self, interface: str = None) -> CommandResponse:
        """
        Returns interface status of one or all switchports.
        """
        string = 'show interface status'
        if interface:
            string = f'{string} {interface}'
        return self.command(string)

    def get_optics(self) -> CommandResponse:
        """
        Returns information about optical transceivers.
        """
        
    def get_lldp(self) -> CommandResponse:
        """
        Returns LLDP neighbor details information.
        """
        return self.command('show lldp neighbor detail')