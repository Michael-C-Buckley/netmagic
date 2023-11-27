# NetMagic Brocade Device Library

# Python Modules
from re import search

# Third-Party Modules

# Local Modules
from netmagic.common.types import Transport
from netmagic.devices.switch import Switch
from netmagic.handlers import CommandResponse, ResponseGroup, get_fsm_data
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

    # CUSTOM FSM METHOD

    # IDENTITY
    def get_running_config(self) -> CommandResponse:
        """
        Returns the running configuration.
        """
        return super().get_running_config()

    def get_interface_status(self, interface: str = None,
                             template: str|bool = None) -> CommandResponse:
        """
        Returns interface status of one or all switchports.
        
        PARAMS:
        `interface`: `str` for the name of getting the full status of a single interface
        `template`: `str` for the path of the TextFSM template to use, else `None`
           will use the default bulit-in, and `False` will skip parsing 
        """
        command_portion = 'brief wide' if interface is None else f'e {interface}'
        int_status = self.command(f'show interfaces {command_portion}')

        if template is False:
            return int_status
        
        template = 'show_int' if interface is None else 'show_single_int'
        fsm_output = get_fsm_data(int_status.response, 'brocade', template)

        for entry in fsm_output:
            if (name := entry.get('name')):
                # Names may may whitespace characters when they should be None
                if not name.strip():
                    entry['name'] = None

        int_status.fsm_output = fsm_output
        return int_status
    
    def get_all_interface_status(self) -> ResponseGroup:
        """
        Returns all the detailed entries for interfaces on the device
        """
    
    def get_media(self, template: str|bool = None) -> CommandResponse:
        """
        Returns the media information on the device

        PARAMS:
        `template`: `str` for the path of the TextFSM template to use, else `None`
           will use the default bulit-in, and `False` will skip parsing 
        """
        media = self.command('show media')

        if template is not False:
            template = 'show_media' if template is None else template
            media.fsm_output = get_fsm_data(media.response, 'brocade', template)

        return media
    
    def get_optics(self, template: str|bool = None) -> ResponseGroup:
        """
        Returns information about optical transceivers.
        """
        media = self.get_media()

        optical_interfaces = []
        for interface in media.fsm_output:
            if search(r'(?i)sfp', interface.get('medium')):
                optical_interfaces.append(interface.get('interface'))
        
        optics = ResponseGroup([self.command(f'show optic {interface}') for interface in optical_interfaces])
        
        if template is not False:
            template = 'show_optic' if template is None else template
            optics_data = [optics_response.response for optics_response in optics.responses]
            optics.fsm_output = get_fsm_data(optics_data, 'brocade', template)
        
        return optics
    
    def get_lldp(self, template: str|bool = None) -> CommandResponse:
        """
        Returns LLDP neighbor details information.
        """
        lldp = self.command('show lldp neighbor detail')
        
        # Cases to skip parsing, lldp only shows up in the response if LLDP is not enabled
        if template is False or search(r'lldp', lldp.response):
            return lldp

        template = 'show_lldp_nei_det' if not template else template
        lldp.fsm_output = get_fsm_data(lldp.response, 'brocade', template, 'Local port')

        return lldp