from mactools import MacAddress

from netmagic.common.classes.interface import InterfaceLLDP
from netmagic.common.classes.status import MACTableEntry


def test_mac_address_v2_inputs_are_normalized():
    expected = "00:11:22:33:44:55"
    addresses = {
        MacAddress(value)
        for value in ("0011.2233.4455", "00-11-22-33-44-55", 0x001122334455)
    }

    assert {str(address) for address in addresses} == {expected}
    assert len(addresses) == 1


def test_models_preserve_existing_mac_address_objects():
    mac = MacAddress("0011.2233.4455")

    lldp = InterfaceLLDP(host="switch", interface="Gi1/0/1", chassis_mac=mac)
    table_entry = MACTableEntry.create(
        "switch",
        mac,
        interface="Gi1/0/1",
        vlan="10",
        type="dynamic",
    )

    assert lldp.chassis_mac is mac
    assert table_entry.mac is mac
