# NetMagic Cisco Device Library

# Python Modules

# Third-Party Modules

# Local Modules
from netmagic.devices.switch import Switch
from netmagic.handlers import CommandResponse, ResponseGroup, get_fsm_data
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
        desc_template = 'show_int_desc' if not desc_template else desc_template

        int_status.fsm_output = get_fsm_data(int_status.response, 'cisco', status_template)
        int_desc.fsm_output = get_fsm_data(int_desc.response, 'cisco', desc_template)

        return ResponseGroup([int_status, int_desc], None, 'Cisco Interface Status')
    
    def get_optics(self, template: str|bool = None) -> CommandResponse:
        """
        Returns information about optical transceivers.
        """
        optics = self.command('show interface transceiver detail')

        if template is not False:
            template = 'show_int_trans_det' if template is None else template
            optics.fsm_output = get_fsm_data(optics.response, 'cisco', template)

        return optics

    def get_lldp(self, template: str|bool = None) -> CommandResponse:
        """
        Returns LLDP neighbor details information.
        """
        lldp = self.command('show lldp neighbor detail')

        if template is not False:
            template = 'show_lldp_nei_det' if template is None else template
            lldp.fsm_output = get_fsm_data(lldp.response, 'cisco', template)
        
        return lldp