from netmagic.devices.network_device import NetworkDevice
from netmagic.devices.router import Router
from netmagic.devices.switch import Switch
from netmagic.devices.universal import Device
from netmagic.devices.vendors.brocade import BrocadeSwitch
from netmagic.devices.vendors.cisco import CiscoIOSSwitch
from netmagic.devices.vendors.cisco_xr import CiscoIOSXRRouter

__all__ = [
    "BrocadeSwitch",
    "CiscoIOSSwitch",
    "CiscoIOSXRRouter",
    "Device",
    "NetworkDevice",
    "Router",
    "Switch",
]
