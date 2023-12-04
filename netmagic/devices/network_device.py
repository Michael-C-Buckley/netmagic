# Project NetMagic Networking Device Library

# Python Module
from datetime import datetime
from re import search
from time import sleep

# Third-Party Modules
from netmiko import ReadTimeout, redispatch

# Local Modules
from netmagic.common.classes import (
    CommandResponse, ConfigResponse, ResponseGroup,
    InterfaceStatus, InterfaceTDR
)
from netmagic.common.types import Engine, Transport, ConfigSet
from netmagic.common.utils import validate_max_tries, unquote
from netmagic.devices.universal import Device
from netmagic.handlers import get_fsm_data
from netmagic.handlers.parse import INTERFACE_REGEX
from netmagic.sessions import Session, TerminalSession, RESTCONFSession, NETCONFSession

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

    def session_preparation(self, dispatch: str = 'generic_termserver'):
        """
        CLI session preparation either for SSH jumping or serial connections
        """
        def redispatch_device(dispatch: str) -> None:
            if self.cli_session.connection.device_type != dispatch:
                redispatch(self.cli_session.connection, dispatch, False)
        
        if self.cli_session.engine == Engine.NETMIKO:
            if self.cli_session.transport == Transport.SERIAL:
                redispatch_device('cisco_ios_serial')
            else:
                redispatch_device(dispatch)

        self.enable()

    def enable(self, password: str = None) -> None:
        """
        Manual entering of enabled mode
        """
        self.command('enable', r'[Pp]assword')
        password = password if password is not None else self.cli_session.secret
        self.command(password)
    
    # CONFIG HANDLING

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
            self.hostname = unquote(hostname_str)
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
        self.not_implemented_error_generic()
        
    def get_lldp(self) -> CommandResponse:
        """
        Returns LLDP neighbor details information.
        """
        return self.command('show lldp neighbor detail')
    
    def get_media(self) -> None:
        """
        Gets transceiver information.
        """
        self.not_implemented_error_generic()

    def get_tdr_data(self, send_tdr_command: str, show_tdr_command: str, vendor: str,
                     interface_status: ResponseGroup|CommandResponse = None,
                     only_bad: bool = True, template: str|bool = None):
        """
        Collects TDR data of interfaces.

        PARAMS:
        `send_tdr_command`: string format of CLI command to submit TDR
        `show_tdr_command`: string format of CLI command to show the submitted TDR result
        `vendor`: string of the vendor name for template lookup
        `interface_status`: Response-form output of the device's interface status for assessment
        `only_bad`: bool for only doing suspected bad cables or all interfaces
        `template`: string entry for the path to a custom TextFSM template
        """
        for command in [send_tdr_command, show_tdr_command]:
            if search(INTERFACE_REGEX, command):
                raise ValueError('TDR commands should not have interfaces in them')
            
        if interface_status is None:
            interface_status = self.get_interface_status()

        template = 'show_tdr' if template is None else template
        submitted_tests: list[str] = []
        responses: list[CommandResponse] = []

        fsm_output: dict[str, InterfaceStatus] = interface_status.fsm_output
        submit_tdr = lambda intf: self.command(f'{send_tdr_command} {intf}')

        # Submit the tests
        for interface in fsm_output.values():
            if only_bad:
                if not isinstance(interface.speed, int):
                    continue
                if interface.media:
                    if search(r'SFP', interface.media):
                        continue
                if interface.speed < 1000:
                    responses.append(submit_tdr(interface.name))
                    submitted_tests.append(interface.name)
            else:
                responses.append(submit_tdr(interface.name))
                submitted_tests.append(interface.name)

        fsm_output = {}
        # Show the test results
        check_tdr = lambda intf: self.command(f'{show_tdr_command} {intf}')
        for interface in submitted_tests:
            tdr_result = check_tdr(interface)
            while search(r'(?i)not complete', tdr_result.response):
                sleep(1)
                tdr_result = check_tdr(interface)
            responses.append(tdr_result)
            # parse, add to object
            if template is not False:
                fsm_data = get_fsm_data(tdr_result.response, vendor, template)
                fsm_output[interface] = InterfaceTDR.create(self.hostname, fsm_data)

        if responses:
            return ResponseGroup(responses, fsm_output, 'TDR Data')