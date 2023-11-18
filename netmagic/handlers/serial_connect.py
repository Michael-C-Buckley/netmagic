# Netmagic Serial Connection Handler

# Python Modules
from serial import SerialException

# Third-Party Modules
import serial.tools.list_ports as list_ports
from netmiko import redispatch
from netmiko import (
    BaseConnection,
    ConnectHandler,
    NetmikoAuthenticationException as AuthException,
)

def serial_connect(serial_port: str, username: str, password: str, secret: str = None,
                   device_type: str = 'generic_termserver') -> BaseConnection:
    """
    Standard Netmiko connection with a serial port instead of SSH.
    """
    profile = {
        'device_type': device_type,
        'serial_settings': {'port': serial_port},
        'username': username,
        'password': password,
        'secret': secret
    }
    try:
        return ConnectHandler(**profile)
    except (AuthException, SerialException) as e:
        # ERROR HANDLING PLANNED
        print(e)
        return e