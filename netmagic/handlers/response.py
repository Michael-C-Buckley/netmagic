from datetime import datetime
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from netmagic.devices.universal import Device

from netmagic.definitions import HostType

class Response:
    """
    Response base class for `BannerResponse` and `CommandResponse`    
    """
    def __init__(self, response: str, sent_time: float, received_time: float) -> None:
        self.response = response
        self.sent_time = sent_time
        self.received_time = received_time
        self.latency = self.received_time - self.sent_time

    def __str__(self) -> str:
        return self.response


class BannerResponse(Response):
    """
    Simple object for capturing the info from a banner grab for identifying devices.
    """
    def __init__(self, response: str, host: HostType, port: int, sent_time: float, received_time: float) -> None:
        self.host = host
        self.port = port
        super().__init__(response, sent_time, received_time)

    def __repr__(self) -> str:
        return f'[{self.host}:{self.port}]: {self.response}'   


class CommandResponse(Response):
    """
    Simple object for capturing info for various details of a Netmiko `command`
    """
    def __init__(self, input: str, response: str, sent_time: datetime,
                 received_time: datetime, output_list: list[tuple[str, datetime, datetime]],
                 device: 'Device', expect_string: str) -> None:
        self.input = input
        self.output_list = output_list
        self.expect_string = expect_string
        self.device = device
        self.result = None
        super().__init__(response, sent_time, received_time)

    def __repr__(self) -> str:
        return f'[{self.device.hostname}] RE: {self.input}'