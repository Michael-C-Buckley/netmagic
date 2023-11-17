# Project NetMagic Response Handler Module

# Python Modules
from datetime import datetime
from typing import TYPE_CHECKING

from ipaddress import (
    IPv4Address as IPv4,
    IPv6Address as IPv6
)

if TYPE_CHECKING:
    from netmagic.devices import Device
    from netmagic.sessions.terminal import TerminalSession

class Response:
    """
    Response base class for `BannerResponse` and `CommandResponse`    
    """
    def __init__(self, response: str, sent_time: datetime,
                 received_time: datetime = None, attempts: int = 1) -> None:
        
        if not received_time:
            received_time = datetime.now()
        
        self.response = response
        self.sent_time = sent_time
        self.received_time = received_time
        self.latency = self.received_time - self.sent_time
        self.retries = attempts

    def __str__(self) -> str:
        return self.response


class BannerResponse(Response):
    """
    Simple object for capturing the info from a banner grab for identifying devices.
    """
    def __init__(self, response: str, host: str|IPv4|IPv6, port: int,
                 sent_time: datetime, received_time: datetime = None) -> None:
        self.host = host
        self.port = port
        super().__init__(response, sent_time, received_time)

    def __repr__(self) -> str:
        return f'[{self.host}:{self.port}]: {self.response}'   


class CommandResponse(Response):
    """
    Simple object for capturing info for various details of a Netmiko `command`
    """
    def __init__(self, response: str, command_string: str, sent_time: datetime,
                session: 'TerminalSession', expect_string: str, success: bool = True,
                received_time: datetime = None, attempts: int = 1) -> None:
        self.command_string = command_string
        self.expect_string = expect_string
        self.session = session
        self.success = success
        
        super().__init__(response, sent_time, received_time, attempts)

    def __repr__(self) -> str:
        # return f'[{self.device.hostname}] RE: {self.command_string}'
        return f'RE({self.session.host}): {self.command_string}'
    
class ConfigResponse(Response):
    """
    Simple objects for capturing info for a CLI configuration
    """
    def __init__(self, response: str, config: str, sent_time: datetime,
                session: 'TerminalSession', success: bool = True,
                received_time: datetime = None, attempts: int = 1) -> None:
        super().__init__(response, sent_time, received_time, attempts)
        self.config_sent = config
        self.session = session
        self.success = success
        
