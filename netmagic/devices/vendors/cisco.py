# NetMagic Cisco Device Library

# Python Modules

# Third-Party Modules

# Local Modules
from netmagic.devices.switch import Switch
from netmagic.common.classes import CommandResponse, ResponseGroup
from netmagic.common.classes.interface import (
    InterfaceStatus, InterfaceOptics, InterfaceLLDP
)
from netmagic.handlers import get_fsm_data
from netmagic.sessions import Session

class CiscoIOSSwitch(Switch):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    # IDENTITY
    def get_running_config(self) -> CommandResponse:
        """
        Returns the running configuration.
        """
        return super().get_running_config()

    def get_interface_status(self, interface: str = None,
                             status_template: str|bool = None,
                             desc_template: str = None) -> CommandResponse|ResponseGroup:
        """
        Returns interface status of one or all switchports.
        """
        int_status = self.command('show interface status')

        if status_template is False:
            return int_status
        
        int_desc = self.command('show interface description')

        status_template = 'show_int_status' if not status_template else status_template
        fsm_status_data = get_fsm_data(int_status.response, 'cisco', status_template)

        desc_template = 'show_int_desc' if not desc_template else desc_template
        fsm_desc_data = get_fsm_data(int_desc.response, 'cisco', desc_template)

        # Parse and combine for full-length interface descriptions
        fsm_output = {i['port']: InterfaceStatus(self.hostname, **i) for i in fsm_status_data}
        for entry in fsm_desc_data:
            fsm_output[entry]['name'] = entry.get('name')

        return ResponseGroup([int_status, int_desc], fsm_output, 'Cisco Interface Status')
    
    def get_optics(self, template: str|bool = None) -> CommandResponse:
        """
        Returns information about optical transceivers.
        """
        optics = self.command('show interface transceiver detail')

        if template is not False:
            template = 'show_int_trans_det' if template is None else template
            fsm_data = get_fsm_data(optics.response, 'cisco', template)
            optics.fsm_output = {i['port']: InterfaceOptics(self.hostname, **i) for i in fsm_data}

        return optics

    def get_lldp(self, template: str|bool = None) -> CommandResponse:
        """
        Returns LLDP neighbor details information.
        """
        lldp = self.command('show lldp neighbor detail')

        if template is not False:
            template = 'show_lldp_nei_det' if template is None else template
            fsm_data = get_fsm_data(lldp.response, 'cisco', template)
            lldp.fsm_output = {i['port']: InterfaceLLDP(self.hostname, **i) for i in fsm_data}
        
        return lldp