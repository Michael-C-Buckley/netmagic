# Netmagic Serial Connection Handler

# Python Modules
from serial import SerialException
from re import search

# Third-Party Modules
import serial.tools.list_ports as list_ports
from netmiko import (
    BaseConnection,
    ConnectHandler,
    NetmikoAuthenticationException as AuthException,
)

def get_serial_ports():
    """
    Filters and finds serial ports that have USB in their description.
    System-agnostic since it programmatically finds serial ports.
    """
    return [port.device for port in list_ports.comports() if search(r'(?i)usb', port.description)]

def serial_connect(port: str, username: str, password: str, secret: str = None,
                   device_type: str = 'cisco_ios_serial', *args, **kwargs) -> BaseConnection:
    """
    Standard Netmiko connection with a serial port instead of SSH.
    """
    profile = {
        'device_type': device_type,
        'serial_settings': {'port': port},
        'username': username,
        'password': password,
        'secret': secret
    }

    try:
        return ConnectHandler(**profile)
    except (AuthException, SerialException) as e:
        # ERROR HANDLING PLANNED
        raise e