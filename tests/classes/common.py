from dataclasses import dataclass

# NetMagic Common Test Items
# Python Modules
from unittest.mock import Mock

# Third-Party Modules
from netmiko import BaseConnection

from netmagic.common import Transport

# Local Modules
from netmagic.sessions.terminal import TerminalSession


# Class to test Netmiko's `BaseConnection`
class MockBaseConnection(Mock):
    __class__ = BaseConnection
    __spec__ = BaseConnection


class MockTerminalSession(Mock):
    __class__ = TerminalSession
    __spec__ = TerminalSession


@dataclass
class TestResponse:
    """
    Simple shell to hold just the attributes needed for testing
    """

    response: str


SSH_KWARGS = {
    "host": "::1",
    "port": 22,
    "username": "admin",
    "password": "admin",  # nosec B105
    "secret": "admin",
    "transport": Transport.SSH,
    "device_type": "generic_termserver",
}
