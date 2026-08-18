# Netmagic Serial Connection Handler

# Python Modules
from re import search

# Third-Party Modules
from netmiko import (
    BaseConnection,
    ConnectHandler,
)
from serial.tools import list_ports


def get_serial_ports():
    """
    Filters and finds serial ports that have USB in their description.
    System-agnostic since it programmatically finds serial ports.
    """
    return [
        port.device
        for port in list_ports.comports()
        if search(r"(?i)usb", port.description)
    ]


def serial_connect(
    port: str,
    username: str,
    password: str,
    secret: str | None = None,
    device_type: str = "cisco_ios_serial",
    *args,
    **kwargs,
) -> BaseConnection:
    """
    Standard Netmiko connection with a serial port instead of SSH.
    """
    profile = {
        "device_type": device_type,
        "serial_settings": {"port": port},
        "username": username,
        "password": password,
        "secret": secret,
    }

    return ConnectHandler(**profile)
