# NetMagic Brocade Device Library

# Python Modules
from re import search

# Third-Party Modules

# Local Modules
from netmagic.common.types import Transport
from netmagic.devices.switch import Switch
from netmagic.handlers import CommandResponse, get_fsm_data
from netmagic.sessions import Session, TerminalSession


class BrocadeSwitch(Switch):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        if isinstance(session, TerminalSession):
            if session.transport == Transport.SERIAL:
                self.session_preparation()
        self.template_path = 'mactools/templates/brocade'

    def session_preparation(self):
        """
        CLI session preparation either for SSH jumping or serial connections
        """
        self.enable()
        self.command('skip-page-display')

    def enable(self, password: str = None):
        """
        Manual entering of enabled mode
        """
        output = self.command('enable', r'[Pp]assword')
        if password is not None:
            self.command(password)

    # IDENTITY
    def get_running_config(self) -> CommandResponse:
        """
        Returns the running configuration.
        """
        return super().get_running_config()

    def get_interface_status(self, interface: str = None) -> list[dict[str, str]]:
        """
        Returns interface status of one or all switchports.
        """
        if interface is None:
            int_status = self.command('show interfaces brief wide')
        else:
            int_status = self.command(f'show interface e {interface}')
        template = 'show_int' if interface is None else 'show_single_int'
        return get_fsm_data(int_status.response, 'brocade', template)
    
    def get_optics(self) -> list[dict[str, str]]:
        """
        Returns information about optical transceivers.
        """
        media = self.command('show media')
        parsed_media = get_fsm_data(media.response, 'brocade', 'show_media')

        optical_interfaces = []
        for interface in parsed_media:
            if search(r'(?i)sfp', interface.get('Medium')):
                optical_interfaces.append(interface.get('Interface'))
        
        optics_data = [self.command(f'show optic {interface}').response for interface in optical_interfaces]
        return get_fsm_data(optics_data, 'brocade', 'show_optic')
    
    def get_lldp(self) -> CommandResponse:
        """
        Returns LLDP neighbor details information.
        """
        return super().get_lldp()