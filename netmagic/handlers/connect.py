from netmiko import BaseConnection, ConnectHandler
from socket import (
    socket, gaierror,
    AF_INET, AF_INET6,
    SOCK_STREAM,
    getaddrinfo
)
from datetime import datetime

from ipaddress import (
    IPv4Address as IPv4,
    IPv6Address as IPv6
)

from netmagic.handlers.response import BannerResponse

def netmiko_connect(host: str|IPv4|IPv6, port: int, username: str, password: str,
                    device_type: str, *args, **kwargs) -> BaseConnection|Exception:
    """
    Standard Netmiko connection variables and environment, mostly used as part of a larger connection scheme.

    Take in the Profile as keyword arguments and returns a Netmiko Base Connection or Netmiko Timeout/Auth Exceptions.
    """
    # Collect input the default named input parameters
    host = str(host)
    connection_profile = {k: v for k, v in locals().items() if k not in ['kwargs', 'args']}

    # Collect the additional user optional parameters
    for key, value in kwargs.items():
        connection_profile[key] = value

    # ADD EXCEPTION HANDLING
    return ConnectHandler(**connection_profile)

def get_device_type(host: str|IPv4|IPv6, port: int = 22) -> BannerResponse:
    """
    Attempts a banner grab on a location to get the device information from 
    the response packet, mostly used as part of a larger connection scheme.

    Returns a custom object `BannerResponse` with details about the connection.
    """
    host = str(host)
    sent_time = datetime.now()
    banner_kwargs = {k:v for k, v in locals().items()}
    try:
        addr_info = getaddrinfo(host, port, type=SOCK_STREAM)
        with socket(addr_info[0][0], SOCK_STREAM) as banner_socket:
            banner_socket.connect((host, int(port)))
            banner = banner_socket.recv(1024).decode('utf-8;', errors='ignore').strip('\n').strip('\r')
    except (TimeoutError, ConnectionRefusedError, gaierror) as e:
        return BannerResponse(e, **banner_kwargs)
    else:
        return BannerResponse(banner, **banner_kwargs)
    