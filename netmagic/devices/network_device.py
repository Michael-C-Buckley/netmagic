# Project NetMagic Networking Device Library

# Local Modules
from netmagic.devices import Device
from netmagic.handlers.response import CommandResponse
from netmagic.sessions.session import Session, RESTCONFSession, NETCONFSession
from netmagic.sessions.terminal import TerminalSession

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

    def not_implemeneted_error_generic(self):
        """
        Error for methods not available on generic network devices
        """
        raise NotImplementedError('Not available for generic network devices')
    
    # CONFIG HANDLING

    def enable_loop(self, password: str = None) -> bool:
        """
        Inner loop for `enable`
        """

    def enable(self) -> bool:
        """
        Manual SSH enable method useful for proxy SSH
        """

    def config_try_loop(self, config: list[str], exit: bool) -> str:
        """
        Inner loop for `send_config`
        """

    def send_config(self, config: list[str], exit: bool = True,
                    *args, **kwargs) -> str:
        """
        Send config
        """

    def write_memory(self):
        return self.cli_session.connection.send_command('write memory')
    
    # IDENTITY AND STATUS

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