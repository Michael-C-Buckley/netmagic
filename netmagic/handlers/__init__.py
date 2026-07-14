from netmagic.handlers.connect import netmiko_connect, get_device_type
from netmagic.handlers.serial_connect import get_serial_ports, serial_connect
from netmagic.handlers.parse import get_fsm_data

__all__ = [
    "get_device_type",
    "get_fsm_data",
    "get_serial_ports",
    "netmiko_connect",
    "serial_connect",
]
