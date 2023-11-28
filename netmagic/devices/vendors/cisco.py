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

    def get_interface_status(self, interface: str = None) -> ResponseGroup:
        """
        Returns interface status of one or all switchports.
        """
        int_desc = self.command('show interface description')
        int_status = self.command('show interface status')
        # Parse and mix these
        return super().get_interface_status(interface)
    
    def get_optics(self, template: str|bool = None) -> CommandResponse:
        """
        Returns information about optical transceivers.
        """
        optics = self.command('show interface transceiver detail')

        if template is not False:
            template = 'show_int_trans_det' if template is None else template
            optics.fsm_output = get_fsm_data(optics.response, 'cisco', template)

        return optics

        return super().get_optics()
    
    def get_lldp(self, template: str|bool = None) -> CommandResponse:
        """
        Returns LLDP neighbor details information.
        """
        lldp = self.command('show lldp neighbor detail')

        if template is not False:
            template = 'show_lldp_nei_det' if template is None else template
            lldp.fsm_output = get_fsm_data(lldp.response, 'cisco', template)
        
        return lldp