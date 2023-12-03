# NetMagic Cisco Device Library

# Python Modules
from re import search
from time import sleep

# Third-Party Modules
from netmiko import redispatch

# Local Modules
from netmagic.common.types import Transport
from netmagic.common.classes import CommandResponse, ResponseGroup
from netmagic.common.classes.interface import (
    InterfaceStatus, InterfaceOptics, InterfaceLLDP,
    InterfaceTDR, TDRStatus
)
from netmagic.devices.switch import Switch
from netmagic.handlers import get_fsm_data
from netmagic.sessions import Session, TerminalSession

class CiscoIOSSwitch(Switch):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        if isinstance(session, TerminalSession):
            if session.transport == Transport.SERIAL:
                self.session_preparation()

    def session_preparation(self):
        """
        CLI session preparation either for SSH jumping or serial connections
        """
        super().session_preparation('cisco_ios')
        self.command('terminal length 0')

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
        fsm_output = {i['port']: InterfaceStatus(host = self.hostname, **i) for i in fsm_status_data}
        for entry in fsm_desc_data:
            fsm_output[entry['interface']].desc = entry['desc'].strip()

        return ResponseGroup([int_status, int_desc], fsm_output, 'Cisco Interface Status')
    
    def get_optics(self, template: str|bool = None) -> CommandResponse:
        """
        Returns information about optical transceivers.
        """
        optics = self.command('show interface transceiver detail')

        if template is not False:
            template = 'show_int_trans_det' if template is None else template
            fsm_data = get_fsm_data(optics.response, 'cisco', template)
            optics.fsm_output = {i['port']: InterfaceOptics(host = self.hostname, **i) for i in fsm_data}

        return optics

    def get_lldp(self, template: str|bool = None) -> CommandResponse:
        """
        Returns LLDP neighbor details information.
        """
        lldp = self.command('show lldp neighbor detail')

        if template is not False:
            template = 'show_lldp_nei_det' if template is None else template
            fsm_data = get_fsm_data(lldp.response, 'cisco', template)
            lldp.fsm_output = {i['port']: InterfaceLLDP(host = self.hostname, **i) for i in fsm_data}
        
        return lldp
    
    def get_tdr_data(self, interface_status: ResponseGroup = None,
                     only_bad: bool = True, template: str|bool = None):
        """
        Collects TDR data of interfaces
        """
        tdr_common = 'cable-diagnostics tdr int'
        send_tdr_command = f'test {tdr_common}'
        show_tdr_command = f'show {tdr_common}'
        if interface_status is None:
            interface_status = self.get_interface_status()

        template = 'show_tdr' if template is None else template
        submitted_tests: list[str] = []
        responses: list[CommandResponse] = []

        fsm_output: dict[str, InterfaceStatus] = interface_status.fsm_output
        submit_tdr = lambda intf: self.command(f'test cable-diagnostics tdr int {intf}')

        # Submit the tests
        for interface in fsm_output.values():
            if only_bad:
                if not isinstance(interface.speed, int):
                    continue
                if search(r'SFP', interface.media):
                    continue
                if interface.speed < 1000:
                    responses.append(submit_tdr(interface.name))
                    submitted_tests.append(interface.name)
            else:
                responses.append(submit_tdr(interface.name))
                submitted_tests.append(interface.name)

        fsm_output = {}
        def process_fsm_data(interface: str, response_str: str) -> InterfaceTDR:
            # Convert and normalize the data into the model
            fsm_data = get_fsm_data(response_str, 'cisco', template)
            tdr_kwargs = {
                'host': self.hostname,
                'port': interface,
            }
            if (speed_match := search(r'\d+[MG]', response_str)):
                tdr_kwargs['speed'] = speed_match.group()

            for line in fsm_data:
                local_pair = line['local_pair']
                remote_pair = line['remote_pair']
                tdr_status = TDRStatus(line['status'])
                distance = line['distance']
                tdr_kwargs[f'pair_{local_pair.lower()}'] = (remote_pair, tdr_status, distance)

            return InterfaceTDR(**tdr_kwargs)

        # Show the test results
        check_tdr = lambda intf: self.command(f'show cable-diagnostics tdr int {intf}')
        for interface in submitted_tests:
            tdr_result = check_tdr(interface)
            while search(r'(?i)not complete', tdr_result.response):
                sleep(1)
                tdr_result = check_tdr(interface)
            responses.append(tdr_result)
            # parse, add to object
            if template is not False:
                fsm_output[interface] = process_fsm_data(interface, tdr_result.response)

        if responses:
            return ResponseGroup(responses, fsm_output, 'Cisco TDRs')