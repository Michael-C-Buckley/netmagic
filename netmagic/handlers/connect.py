# Project NetMagic Connection Handler Module

# Python Modules
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime
from re import search
from time import sleep
from socket import socket, gaierror, SOCK_STREAM, getaddrinfo

# Third-Party Modules
from netmiko import BaseConnection, ConnectHandler

# Local Modules
from netmagic.common.classes import BannerResponse, ConnectResponse
from netmagic.common.types import HostT

successful_credentials: list[tuple[str, str]] = []

def get_device_type(host: HostT, port: int = 22, timeout: int = 10) -> BannerResponse:
    """
    Attempts a banner grab on a location to get the device information from 
    the response packet, mostly used as part of a larger connection scheme.

    Returns a custom object `BannerResponse` with details about the connection.
    """
    host = str(host)
    sent_time = datetime.now()
    banner_kwargs = {**locals()}
    try:
        addr_info = getaddrinfo(host, port, type=SOCK_STREAM)
        with socket(addr_info[0][0], SOCK_STREAM) as open_socket:
            open_socket.settimeout(timeout)
            open_socket.connect((host, int(port)))
            banner = open_socket.recv(1024).decode('utf-8;', errors='ignore').strip('\n').strip('\r')
    except (TimeoutError, ConnectionRefusedError, gaierror) as e:
        return BannerResponse(e, **banner_kwargs)
    else:
        return BannerResponse(banner, **banner_kwargs)

def netmiko_connect(host: HostT, port: int, username: str, password: str,
                    device_type: str, *args, **kwargs) -> BaseConnection|Exception:
    """
    Standard Netmiko connection variables and environment, mostly used as part of a larger connection scheme.

    Take in the Profile as keyword arguments and returns a Netmiko Base Connection or Netmiko Timeout/Auth Exceptions.
    """
    # Collect input the default named input parameters and exclude *args, **kwargs
    host = str(host)
    connect_kwargs = {k: v for k, v in locals().items() if not search(r'args', k)}

    # Collect the additional user optional parameters
    for key, value in kwargs.items():
        connect_kwargs[key] = value

    return ConnectHandler(**connect_kwargs)

def brute_force(usernames: list[str], passwords: list[str], host: HostT, port: int = 22,
                device_type: str = None, bypass: bool = False):
    """"""

    creds = [(username, password) for username in usernames for password in passwords]

    if not bypass:
        creds = successful_credentials + creds

    for username, password in creds:
        ssh = netmiko_connect(host, port, username, password, device_type)
        if isinstance(ssh, BaseConnection):
            return ssh


def distributed_brute_force(hosts: list[tuple[HostT, int, str|None]], usernames: list[str] = None,
                            passwords: list[str] = None, creds: list[tuple[str, str]] = None) -> list[ConnectResponse]:
    """
    Brute forcer for a group of devices with a shared set of credentials that will spread the attempts
    per credential across the group of devices to find faster resolution
    """
    successes: list[ConnectResponse] = []
    failures: list[ConnectResponse] = []
    futures: dict[Future, ConnectResponse] = {}
    if not creds and usernames and passwords:
        creds = ((username, password) for username in usernames for password in passwords)
    
    while True:
        with ThreadPoolExecutor(len(hosts)) as executor:
            if not creds:
                break
            elif hosts and creds:
                host, port, device_type = hosts.pop(0)
                username, password = creds.pop(0)
                connect_args = (host, port, username, password, device_type)
                future = executor.submit(netmiko_connect, *connect_args)
                futures[future] = ConnectResponse(None, netmiko_connect, connect_args, datetime.now())
            elif not hosts and creds:
                sleep(1)

            for future in as_completed(futures):
                connection = futures[future]
                connection.update_latency(received_time=datetime.now())

                try:
                    connection.response = future.result()
                    successes.append(connection)

                except:
                    connection.response = False
                    failures.append(connection)
                    host, port, _, _, device_type = connection.params
                    hosts.append((host, port, device_type))

    return successes