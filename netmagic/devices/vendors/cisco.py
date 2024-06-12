# NetMagic Cisco Device Library

# Local Modules
from netmagic.common.types import Vendors, SFPAlert
from netmagic.common.classes import (
    CommandResponse, ResponseGroup, SVI,
    InterfaceOptics, InterfaceStatus, InterfaceLLDP, 
    InterfaceVLANs, OpticStatus,
)
from netmagic.common.utils import abbreviate_interface, get_param_names, sort_interfaces
from netmagic.devices.switch import Switch
from netmagic.sessions import Session


class CiscoIOSSwitch(Switch):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.vendor = Vendors.CISCO

    def session_preparation(self):
        """
        CLI session preparation either for SSH jumping or serial connections
        """
        super().session_preparation('cisco_ios')
        self.command('terminal length 0')

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
        fsm_status_data = self.fsm_parse(int_status.response, status_template)

        desc_template = 'show_int_desc' if not desc_template else desc_template
        fsm_desc_data = self.fsm_parse(int_desc.response, desc_template)

        # Parse and combine for full-length interface descriptions
        fsm_output = {i['port']: InterfaceStatus(host = self.hostname, **i) for i in fsm_status_data}
        for entry in fsm_desc_data:
            fsm_output[entry['port']].desc = entry['desc'].strip()

        return ResponseGroup([int_status, int_desc], fsm_output, 'Cisco Interface Status')
    
    def get_optics(self, template: str|bool = None) -> CommandResponse:
        """
        Returns information about optical transceivers.
        """
        optics = self.command('show interface transceiver detail')

        if template is False:
            return optics
        
        optics.fsm_output = {}
        template = 'show_int_trans_det' if template is None else template
        fsm_data = self.fsm_parse(optics.response, template, flatten_key='port')
        root_key_list = ['temperature', 'voltage', 'current', 'transmit_power', 'receive_power']

        for entry in fsm_data:
            port = entry['port']
            port_dict = {'port': port}

            for root_key in root_key_list:
                primary_value = float(entry[root_key])

                def create_values(low_value, high_value):
                    if isinstance(low_value, str):
                        low_value = float(entry[f'{root_key}_{low_value}'])
                    if isinstance(high_value, str):
                        high_value = float(entry[f'{root_key}_{high_value}'])
                    return (low_value, high_value)

                ranges_dict = {
                    SFPAlert.NORMAL: create_values('low_warning', 'high_warning'),
                    SFPAlert.LOW_WARN: create_values('low_alarm', 'low_warning'),
                    SFPAlert.HIGH_WARN: create_values('high_warning', 'high_alarm'),
                    SFPAlert.LOW_ALARM: create_values(float('-inf'), 'low_alarm'),
                    SFPAlert.HIGH_ALARM: create_values('high_alarm', float('inf')),
                }
                # Prepare the ranges for analysis
                for status, values in ranges_dict.items():
                    if values[0] <= primary_value < values[1]:
                        port_dict[root_key] = OpticStatus(reading=primary_value, status=status)
            
            optics.fsm_output[port] = InterfaceOptics(host = self.hostname, **port_dict)

        return optics

    def get_lldp(self, template: str|bool = None) -> CommandResponse:
        """
        Returns LLDP neighbor details information.
        """
        lldp = self.command('show lldp neighbor detail')

        if template is not False:
            template = 'show_lldp_nei_det' if template is None else template
            fsm_data = self.fsm_parse(lldp.response, template)
            raw_output = {i['port']: InterfaceLLDP(host=self.hostname, **i) for i in fsm_data}
            lldp.fsm_output = {i: raw_output[i] for i in sort_interfaces(raw_output)}

        return lldp
    
    def get_tdr_data(self, interface_status: ResponseGroup = None,
                     only_bad: bool = True, template: str|bool = None):
        """
        Collects TDR data of interfaces
        """
        input_kwargs = {k:v for k,v in locals().items() if k in get_param_names(self.get_tdr_data)}

        tdr_common = 'cable-diagnostics tdr int'
        
        additional_kwargs = {
            'send_tdr_command': f'test {tdr_common}',
            'show_tdr_command': f'show {tdr_common}',
        }

        response = super().get_tdr_data(**input_kwargs, **additional_kwargs)
        if response:
            response.description = f'{self.hostname} TDR'
            return response
        
    def get_poe_status(self, template: str|bool = None) -> CommandResponse:
        """
        Returns the POE information of the switch.

        `template` is the path to a custom TextFSM template.  `None` will use the 
        library default version.
        """
        template = 'show_poe' if template is None else template
        return super().get_poe_status('show power inline', template)
    
    def get_mac_table(self, template: str | bool = None) -> CommandResponse:
        show_command = 'show mac address-table'
        return super().get_mac_table(show_command, template)
    
    def get_interface_vlans(self, template: str|bool = None) -> dict[str, InterfaceVLANs|SVI]:
        """
        Returns the VLAN information of the switchports.

        `template` is the path to a custom TextFSM template.  `None` will use the 
        library default version.
        """
        template = 'show_run_vlans' if template is None else template
        fsm_data = self.fsm_parse(self.get_running_config().response, template)
        results: dict[InterfaceVLANs|SVI] = {}

        for line in fsm_data:
            interface = abbreviate_interface(line['interface'])

            kwargs = {k:v for k,v in line.items() if v}
            kwargs['interface'] = interface 

            if kwargs.get('ip_address'):
                results[interface] = SVI(host=self.hostname, **kwargs)
            elif kwargs.get('access') or kwargs.get('trunk'):
                results[interface] = InterfaceVLANs(host=self.hostname, **kwargs)

        return results
