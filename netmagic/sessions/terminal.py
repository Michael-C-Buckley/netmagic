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

class TerminalSession(Session):
    """
    Container for Terminal-based CLI session on SSH, Telnet, serial, etc.
    """
    def __init__(self, host: str|IPv4|IPv6, username: str, password: str,
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

    def command_try_loop(self, command_string: str, expect_string: str = None,
                         read_timeout: float = 10.0, *args, **kwargs) -> str|Exception:
        """
        """
        command_kwargs = {k:v for k,v in locals().items() if k not in ['args', 'kwargs', 'self']}
        command_kwargs = {**kwargs, **command_kwargs}
        try:
            return self.connection.send_command(*args, **command_kwargs)
        except ReadTimeout as e:
            return e

    def command(self, command_string: str|list[str], expect_string: str = None,
                blind: bool = False, max_tries: int = 3, *args, **kwargs) -> CommandResponse:
        """
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

        # Handle enable if needed

        if blind:
            self.connection.write_channel(f'{command_string}\n')
            response = CommandResponse('Blind: True', success=None, **response_kwargs)
            self.command_log.append(response)
            return response

        def execute_command():
            output = self.command_try_loop(**command_kwargs, **kwargs)
            success = False if isinstance(output, Exception) else True
            response = CommandResponse(output, success=success, **response_kwargs)
            self.command_log.append(response)
            return response

        for i in range(max_tries):
            response = execute_command()
            if isinstance(response.response, str):
                break
            if isinstance(response.response, Exception):
                if not self.check_session():
                    raise AttributeError(no_session_string)
        
        return response
