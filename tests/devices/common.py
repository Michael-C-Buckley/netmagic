SWITCH_PATH = ''

from typing import Any

from netmagic.common.classes.interface import InterfaceVLANs, SVI

def prepare_vlan_test_data(vlan_info_parts: dict[str, Any]):
    """
    Manually prepared case data for switch VLAN testing
    """
    interface_vlans = {}
    for interface, kwargs in vlan_info_parts.items():
        common_kwargs = {'host': 'TEST-HOST', 'interface': interface}
        local_class = SVI if 'Vl' in interface else InterfaceVLANs
        interface_vlans[interface] = local_class(**common_kwargs, **kwargs)
    return interface_vlans
