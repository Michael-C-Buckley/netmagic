# NetMagic Brocade Device Library

# Python Modules
from re import search, sub

# Local Modules
from netmagic.common.types import Transport, Vendors
from netmagic.common.classes import (
    CommandResponse, ResponseGroup, InterfaceOptics,
    InterfaceStatus, InterfaceLLDP
)
from netmagic.common.utils import get_param_names
from netmagic.devices.switch import Switch
from netmagic.sessions import Session


class BrocadeSwitch(Switch):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.vendor = Vendors.BROCADE

    def session_preparation(self):
        """
        CLI session preparation either for SSH jumping or serial connections
        """
        super().session_preparation('brocade_fastiron')
        self.command('skip-page-display')

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
           will use the default built-in, and `False` will skip parsing 
        """
        command_portion = 'brief wide' if interface is None else f'e {interface}'
        int_status = self.command(f'show interface {command_portion}')

        if template is False:
            return int_status
        
        template = 'show_int' if interface is None else 'show_single_int'
        fsm_data = self.fsm_parse(int_status.response, template)
        int_status.fsm_output = {i['port']: InterfaceStatus(host = self.hostname, **i) for i in fsm_data}
        
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
           will use the default built-in, and `False` will skip parsing 
        """
        media = self.command('show media')

        if template is not False:
            template = 'show_media' if template is None else template
            media.fsm_output = self.fsm_parse(media.response, template)

        return media
    
    def get_optics(self, template: str|bool = None) -> ResponseGroup:
        """
        Returns information about optical transceivers.
        """
        media = self.get_media()
        optical_interfaces = [i['interface'] for i in media.fsm_output if search(r'(?i)sfp', i['medium'])]
        
        optics_responses = [self.command(f'show optic {intf}') for intf in optical_interfaces]
        optics = ResponseGroup(optics_responses, None, 'Brocade Optics Data')
        
        if template is not False:
            template = 'show_optic' if template is None else template
            optics_data = [optics_response.response for optics_response in optics.responses]
            fsm_data = self.fsm_parse(optics_data, template)
            optics.fsm_output = {i['port']: InterfaceOptics.create(self.hostname, **i) for i in fsm_data}

        return optics
    
    def get_lldp(self, template: str|bool = None) -> CommandResponse:
        """
        Returns LLDP neighbor details information.
        """
        lldp = self.command('show lldp neighbor detail')

        # Cases to skip parsing, lldp only shows up in the response if LLDP is not enabled
        if template is False or search(r'lldp', lldp.response):
            return lldp
        
        # Fix anything that has a multi-line field and adding an end record designator
        lldp.response = sub(r'\\\n\s+', '', lldp.response).replace('\n\n','\nEND\n')

        # The built-in template REQUIRES the above pre-processing to work correctly
        template = 'show_lldp_nei_det' if not template else template
        fsm_data = self.fsm_parse(lldp.response, template)
        lldp.fsm_output = {i['port']: InterfaceLLDP(host = self.hostname, **i) for i in fsm_data}

        return lldp
    
    def get_tdr_data(self, interface_status: CommandResponse = None,
                     only_bad: bool = True, template: str|bool = None):
        """
        Collects TDR data of interfaces
        """
        input_kwargs = {k:v for k,v in locals().items() if k in get_param_names(self.get_tdr_data)}

        tdr_common = 'cable-diagnostics tdr'

        additional_kwargs = {
            'send_tdr_command': f'phy {tdr_common}',
            'show_tdr_command': f'show {tdr_common}',
        }

        response = super().get_tdr_data(**input_kwargs, **additional_kwargs)
        if response:
            response.description = f'{self.hostname} TDR'
            return response
        
    def get_poe_status(self, template: str|bool = None) -> CommandResponse:
        template = 'show_poe' if template is None else template
        return super().get_poe_status('show poe', template)
    
    def get_mac_table(self, template: str | bool = None) -> CommandResponse:
        show_command = 'show mac-address'
        return super().get_mac_table(show_command, template)