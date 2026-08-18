# Project NetMagic Connection Handler Module

# Python Modules
from datetime import UTC, datetime
from re import search
from socket import SOCK_STREAM, gaierror, getaddrinfo, socket

# Third-Party Modules
from netmiko import BaseConnection, ConnectHandler

# Local Modules
from netmagic.common.classes import BannerResponse
from netmagic.common.types import HostT

successful_credentials: list[tuple[str, str]] = []


def get_device_type(host: HostT, port: int = 22, timeout: int = 10) -> BannerResponse:
    """
    Attempts a banner grab on a location to get the device information from
    the response packet, mostly used as part of a larger connection scheme.

    Returns a custom object `BannerResponse` with details about the connection.
    """
    host = str(host)
    sent_time = datetime.now(UTC)
    banner_kwargs = {**locals()}
    try:
        addr_info = getaddrinfo(host, port, type=SOCK_STREAM)
        with socket(addr_info[0][0], SOCK_STREAM) as open_socket:
            open_socket.settimeout(timeout)
            open_socket.connect((host, int(port)))
            banner = (
                open_socket.recv(1024)
                .decode("utf-8;", errors="ignore")
                .strip("\n")
                .strip("\r")
            )
    except (TimeoutError, ConnectionRefusedError, gaierror) as e:
        return BannerResponse(e, **banner_kwargs)
    else:
        return BannerResponse(banner, **banner_kwargs)


def netmiko_connect(
    host: HostT,
    port: int,
    username: str,
    password: str,
    device_type: str,
    ssh_strict: bool = True,
    *args,
    **kwargs,
) -> BaseConnection | Exception:
    """
    Standard Netmiko connection variables and environment, mostly used as part of a larger connection scheme.

    Take in the Profile as keyword arguments and returns a Netmiko Base Connection or Netmiko Timeout/Auth Exceptions.
    """
    # Collect input the default named input parameters and exclude *args, **kwargs
    host = str(host)
    connect_kwargs = {k: v for k, v in locals().items() if not search(r"args", k)}

    # Collect the additional user optional parameters
    for key, value in kwargs.items():
        connect_kwargs[key] = value

    return ConnectHandler(**connect_kwargs)
