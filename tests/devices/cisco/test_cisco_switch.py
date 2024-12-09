
from dataclasses import dataclass
from unittest import TestCase, main
from unittest.mock import Mock, patch


from netmagic.devices import CiscoIOSSwitch
from netmagic.common.types import SwitchportMode

from tests.classes.common import TestResponse
from tests.devices.common import prepare_vlan_test_data


VLAN_INFO = '''
interface GigabitEthernet1/0/1
 description TEST-TRUNK
 switchport trunk native vlan 200
 switchport trunk allowed vlan 10,50,120,200
 switchport mode trunk
!
interface GigabitEthernet1/0/2
 description TEST-ACCESS
 switchport access vlan 120
 switchport mode access
!
interface Vlan100
 ip address 192.0.2.2 255.255.255.0
!'''

CISCO_PATH = 'netmagic.devices.vendors.cisco'
CISCO_SWITCH_PATH = f'{CISCO_PATH}.CiscoIOSSwitch'

class TestCiscoSwitch(TestCase):

    @patch(f'{CISCO_SWITCH_PATH}.get_running_config')
    def test_vlan_parsing(self, patched_method):
        """
        Test to check Cisco collection and parsing of VLANs from the running config
        """
        patched_method.return_value = TestResponse(VLAN_INFO)
        test_switch = CiscoIOSSwitch(Mock())
        test_switch.hostname = 'TEST-HOST'

        vlan_info_parts = {
            'Gi1/0/1': {'native': 200, 'mode': SwitchportMode('trunk'), 'trunk': '10,50,120,200'},
            'Gi1/0/2': {'access': 120, 'mode': SwitchportMode('access')},
            'Vl100': {'ip_address': '192.0.2.2', 'subnet': '255.255.255.0'}
        }

        self.assertEqual(test_switch.get_interface_vlans(), prepare_vlan_test_data(vlan_info_parts))


if __name__ == '__main__':
    main()
