# Project NetMagic Terminal Session Module

# Python Modules
from datetime import datetime
from time import sleep
from typing import Any

from ipaddress import (
    IPv4Address as IPv4,
    IPv6Address as IPv6,
)

# Third-Party Modules
from netmiko import (
    BaseConnection, ReadTimeout,
    NetmikoAuthenticationException,
)

# Local Modules
from netmagic.sessions.session import Session
from netmagic.handlers.response import CommandResponse
from netmagic.handlers.connect import netmiko_connect
from netmagic.common.types import HostT

class TerminalSession(Session):
    """
    Container for Terminal-based CLI session on SSH, Telnet, serial, etc.
    """
    def __init__(self, host: HostT, username: str, password: str,
                 device_type: str, connection: BaseConnection = None,
                 secret: str = None, port: int = 22, engine: str = 'netmiko',
                 *args, **kwargs) -> None:
        super().__init__(host, username, password, port, connection)
        self.secret = secret
        self.engine = engine
        self.device_type = device_type

        # Collect the remaining kwargs to offer when reconnecting
        self.connection_kwargs = {**kwargs}
        
        self.command_log: list[CommandResponse] = []

    # CONNECTION HANDLING

    def connect(self, max_tries: int = 1, username: str = None, password: str = None,
                connect_kwargs: dict[str, Any] = None) -> bool:
        """
        Connect SSH session using the selected attributes.
        Returns `bool` on success or failure.
        """

        if isinstance(self.connection, BaseConnection):
            if self.check_session():
                return True

        max_tries = int(max_tries)
        if max_tries > 1:
            raise ValueError('`max_tries` count must be `1` or greater.')

        # Gather connection information from the session
        attribute_filter = ['host','port','username','password','device_type']
        local_connection_kwargs = {k:v for k,v in self.__dict__.items() if k in attribute_filter}

        if password:
            local_connection_kwargs['password'] = password
        if username:
            local_connection_kwargs['username'] = username
        if self.connection_kwargs and not connect_kwargs:
            local_connection_kwargs.update(self.connection_kwargs)
        if connect_kwargs:
            local_connection_kwargs.update(connect_kwargs)

        for attempt in range(max_tries):
            try:
                self.connection = netmiko_connect(**local_connection_kwargs)
                return True
            except NetmikoAuthenticationException:
                self.connection = None
                if attempt < max_tries:
                    sleep(5)
        return False

    def disconnect(self):
        self.connection.disconnect()
        super().disconnect()

    def check_session(self, escape_attempt: bool = True,
                      reconnect: bool = True) -> bool:
        """
        Determines if the session is good.
        `attempt_escape` will attempt to back out of the current context.
        `reconnect` will automatically replace the session if bad.
        """
        if escape_attempt:
            for i in range(3):
                for char in ['\x1B', '\x03']:
                    self.connection.write_channel(char)
                
        if self.connection.is_alive():
            return True
        else:
            if reconnect:
                return self.connect()

    def get_hostname(self) -> str:
        """
        Generic stand-in that returns the prompt for non-specific devices
        """
        if isinstance(self.connection, BaseConnection):
            return self.connection.find_prompt()
    
    # COMMANDS

    def command(self, command_string: str|list[str], expect_string: str = None,
                blind: bool = False, max_tries: int = 3, read_timeout: int = 10,
                *args, **kwargs) -> CommandResponse:
        """
        Send a command to the command line.

        Params:
        *command_string: the actual string to be transmitted
        *expect_string: regex strings the automation will yield console on detection
        *blind: console will not wait for a response if true
        *max_tries: amount of times re-transmission will be attempted on failure
        *read_timeout: how long the console waits for the expects_string before exception
        """
        max_tries = int(max_tries)
        no_session_string = 'Unable to connect a session to send command'

        if max_tries < 1:
            raise ValueError('`max_tries` count must be `1` or greater.')
        
        if not self.connection:
            if not self.connect():
                raise AttributeError(no_session_string)

        base_kwargs = {
            'command_string': command_string,
            'expect_string': expect_string,
        }

        response_kwargs = {
            **base_kwargs,
            'sent_time': datetime.now(),
            'session': self,
        }

        command_kwargs = {
            **base_kwargs,
            **kwargs,
        }

        if blind:
            self.connection.write_channel(f'{command_string}\n')
            response = CommandResponse('Blind: True', **response_kwargs)
            self.command_log.append(response)
            return response

        # Begin execution
        for i in range(max_tries):

            try:
                output = self.connection.send_command(*args, **command_kwargs)
            except ReadTimeout as e:
                output = e

            response = CommandResponse(output, **response_kwargs, attempts=i+1)
            self.command_log.append(response)

            if isinstance(response.response, str):
                break
            if isinstance(response.response, Exception):
                if not self.check_session():
                    raise AttributeError(no_session_string)
        
        return response
