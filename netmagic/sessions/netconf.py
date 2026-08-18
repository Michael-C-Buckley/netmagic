# NetMagic NETCONF Session

# Python Modules
from datetime import UTC, datetime
from time import sleep
from typing import Any

# Third-Party Modules
from ncclient import manager
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import AuthenticationError, TransportError

# Local Modules
from netmagic.common import HostT, KwDict, Transport, validate_max_tries
from netmagic.common.classes import NETCONFResponse

# Local Modules
from netmagic.sessions.session import Session


class NETCONFSession(Session):
    """
    Container for NETCONF Session via `ncclient`
    """

    def __init__(
        self,
        host: HostT,
        username: str,
        password: str,
        port: int = 830,
        connection: Any | None = None,
        transport: Transport = Transport.NETCONF,
        **kwargs,
    ) -> None:
        super().__init__(host, username, password, port, connection, transport)
        self.connection_kwargs = {**kwargs}
        self.rpc_log: list[NETCONFResponse] = []

    @validate_max_tries
    def connect(
        self,
        max_tries: int = 1,
        username: str | None = None,
        password: str | None = None,
        connect_kwargs: KwDict | None = None,
    ) -> bool:
        """Connect or reuse an active NETCONF session."""
        if self.check_session():
            return True

        local_connection_kwargs = {
            "host": self.host,
            "port": self.port,
            "username": username or self.username,
            "password": password or self.password,
            **self.connection_kwargs,
        }
        if connect_kwargs:
            local_connection_kwargs.update(connect_kwargs)

        self.connection = None
        for attempt in range(max_tries):
            try:
                self.connection = manager.connect(**local_connection_kwargs)
                return True
            except (AuthenticationError, TransportError):
                self.connection = None
                if attempt + 1 < max_tries:
                    sleep(5)
        return False

    def check_session(self) -> bool:
        """Return whether the current manager reports an active connection."""
        return bool(self.connection and getattr(self.connection, "connected", False))

    def disconnect(self) -> None:
        """Close an active session; repeated calls are safe."""
        connection = self.connection
        try:
            if connection is not None and getattr(connection, "connected", False):
                connection.close_session()
        finally:
            super().disconnect()

    @validate_max_tries
    def get(
        self,
        rpc_filter: object | None = None,
        max_tries: int = 3,
    ) -> NETCONFResponse:
        """Run an idempotent NETCONF get operation."""
        no_session_string = "Unable to connect a NETCONF session for get"
        if not self.check_session() and not self.connect():
            raise AttributeError(no_session_string)

        response: str | Exception
        sent_time = datetime.now(UTC)
        for attempt in range(max_tries):
            connection = self.connection
            if connection is None:
                raise AttributeError(no_session_string)
            try:
                reply = connection.get(filter=rpc_filter)
                response = reply.data_xml
                break
            except TimeoutExpiredError as error:
                response = error
            except TransportError as error:
                response = error
                self.connection = None
                if attempt + 1 < max_tries and not self.connect():
                    raise AttributeError(no_session_string) from error
            except RPCError as error:
                response = error
                break

        result = NETCONFResponse(
            response=response,
            operation="get",
            rpc_filter=rpc_filter,
            sent_time=sent_time,
            session=self,
            attempts=attempt + 1,
        )
        self.rpc_log.append(result)
        return result
