
from dataclasses import dataclass
from unittest import TestCase, main
from unittest.mock import Mock, patch
from typing import Any


from netmagic.devices import BrocadeSwitch
from netmagic.common.types import SwitchportMode

from tests.classes.common import TestResponse
from tests.devices.common import prepare_vlan_test_data


VLAN_INFO = '''
vlan 1 name DEFAULT-VLAN by port
!
vlan 50 name TEST1 by port
 tagged ethe 1/1/1 ethe 1/1/2
 untagged ethe 1/1/3
!
vlan 100
 tagged ethe 1/1/1 to 1/1/2 
!'''

BROCADE_PATH = 'netmagic.devices.vendors.brocade'
BROCADE_SWITCH_PATH = f'{BROCADE_PATH}.BrocadeSwitch'

class TestCiscoSwitch(TestCase):

    @patch(f'{BROCADE_SWITCH_PATH}.get_running_config')
    def test_vlan_parsing(self, patched_method):
        """
        Test to check Brocade collection and parsing of VLANs from the running config
        """
        patched_method.return_value = TestResponse(VLAN_INFO)
        test_switch = BrocadeSwitch(Mock())
        test_switch.hostname = 'TEST-HOST'

        vlan_info_parts = {
            '1/1/1': {'mode': SwitchportMode('trunk'), 'trunk': '50,100'},
            '1/1/2': {'mode': SwitchportMode('trunk'), 'trunk': '50,100'},
            '1/1/3': {'untags': '50', 'mode': SwitchportMode('access')}
        }

        self.assertEqual(test_switch.get_interface_vlans(), prepare_vlan_test_data(vlan_info_parts))

if __name__ == '__main__':
    main()
