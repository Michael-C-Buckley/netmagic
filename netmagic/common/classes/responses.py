# Project NetMagic Responses

# Python Modules
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netmagic.sessions.terminal import TerminalSession
from netmagic.common.types import HostT, FSMOutputT
    

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


class ResponseGroup:
    """
    Collection of responses
    """
    def __init__(self, responses: list[Response], fsm_output: FSMOutputT = None,
                 description: str = '') -> None:
        self.responses = responses
        self.fsm_output = fsm_output
        self.time_delta = self.find_time_delta()

        # Custom user entered field for `__repr__`
        self.description = description

    def __repr__(self) -> str:
        return f'Response Group({len(self.responses)} members): {self.description}'
    
    def find_time_delta(self):
        sent_times = [response.sent_time for response in self.responses]
        received_time = [response.received_time for response in self.responses]
        return max(received_time) - min(sent_times)


class BannerResponse(Response):
    """
    Simple object for capturing the info from a banner grab for identifying devices.
    """
    def __init__(self, response: str, host: HostT, port: int,
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
    def __init__(self, response: str|Exception, command_string: str, sent_time: datetime,
                session: 'TerminalSession', expect_string: str, success: bool = None,
                received_time: datetime = None, attempts: int = 1,
                fsm_output: FSMOutputT = None) -> None:
        self.command_string = command_string
        self.expect_string = expect_string
        self.session = session
        self.fsm_output = fsm_output

        # Automatic identification based on type
        success_map = {str: True, Exception: False}
        self.success = success_map.get(type(response)) if success is None else success
        
        super().__init__(response, sent_time, received_time, attempts)

    def __repr__(self) -> str:
        return f'RE({self.session.host}): {self.command_string}'
    

class ConfigResponse(Response):
    """
    Simple objects for capturing info for a CLI configuration
    """
    def __init__(self, response: str, config: str, sent_time: datetime,
                session: 'TerminalSession', success: bool = None,
                received_time: datetime = None, attempts: int = 1) -> None:
        super().__init__(response, sent_time, received_time, attempts)
        self.config_sent = config
        self.session = session
        
        # Automatic identification based on type
        success_map = {str: True, Exception: False}
        self.success = success_map.get(type(response)) if success is None else success
        
