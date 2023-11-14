from netmiko import BaseConnection, ConnectHandler
from socket import socket, gaierror, AF_INET, AF_INET6, SOCK_STREAM
from time import perf_counter, time

from ipaddress import (
    IPv4Address as IPv4,
    IPv6Address as IPv6
)

from netmagic.definitions import HostType
from netmagic.handlers.response import BannerResponse

def netmiko_connect(host: HostType, port: int, username: str, password: str,
                    device_type: str, *args, **kwargs) -> BaseConnection|Exception:
    """
    Standard Netmiko connection variables and environment, mostly used as part of a larger connection scheme.

    Take in the Profile as keyword arguments and returns a Netmiko Base Connection or Netmiko Timeout/Auth Exceptions.
    """
    # Collect input the default named input parameters
    connection_profile = {k: v for k, v in locals().items() if k not in ['kwargs', 'args']}

    # Collect the additional user optional parameters
    for key, value in kwargs.items():
        connection_profile[key] = value

    # ADD EXCEPTION HANDLING
    return ConnectHandler(**connection_profile)

def get_device_type(host: HostType, port: int = 22) -> BannerResponse:
    """
    Attempts a banner grab on a location to get the device information from 
    the response packet, mostly used as part of a larger connection scheme.

    Returns a custom object `BannerResponse` with details about the connection.
    """
    banner_kwargs = {k:v for k, v in locals().items()}
    try:

        inet_map = {
            IPv4: AF_INET,
            IPv6: AF_INET6
        }
        
        s = socket(inet_map.get(type(host)), SOCK_STREAM)
        banner_kwargs['sent_time'] = time()
        s.connect((str(host), int(port)))
        banner = s.recv(1024).decode('utf-8;', errors='ignore').strip('\n').strip('\r')
        banner_kwargs['received_time'] = perf_counter()
        s.close()
    except (TimeoutError, ConnectionRefusedError, gaierror) as e:
        banner_kwargs['received_time'] = perf_counter()
        return BannerResponse(e, **banner_kwargs)
    else:
        return BannerResponse(banner, **banner_kwargs)
    