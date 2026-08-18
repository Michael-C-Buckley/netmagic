# NetMagic NETCONF Session Tests

from unittest import TestCase
from unittest.mock import Mock, patch

from ncclient.operations.errors import TimeoutExpiredError
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import TransportError
from ncclient.xml_ import to_ele

from netmagic.common import Transport
from netmagic.common.classes import NETCONFResponse
from netmagic.sessions import NETCONFSession

NETCONF_KWARGS = {
    "host": "192.0.2.1",
    "username": "admin",
    "password": "password",  # nosec B105
}


class TestNETCONFSession(TestCase):
    def test_defaults_and_connection_reuse(self):
        connection = Mock(connected=True)
        session = NETCONFSession(connection=connection, **NETCONF_KWARGS)

        self.assertEqual(session.port, 830)
        self.assertEqual(session.transport, Transport.NETCONF)
        with patch("netmagic.sessions.netconf.manager.connect") as connect:
            self.assertTrue(session.connect())
            connect.assert_not_called()

    def test_connect_and_idempotent_disconnect(self):
        connection = Mock(connected=True)
        session = NETCONFSession(**NETCONF_KWARGS)

        with patch(
            "netmagic.sessions.netconf.manager.connect", return_value=connection
        ) as connect:
            self.assertTrue(session.connect())
            connect.assert_called_once_with(port=830, **NETCONF_KWARGS)

        session.disconnect()
        session.disconnect()
        connection.close_session.assert_called_once_with()
        self.assertIsNone(session.connection)

    def test_get_reconnects_and_retries_safely(self):
        failed_connection = Mock(connected=True)
        failed_connection.get.side_effect = TransportError("closed")
        good_connection = Mock(connected=True)
        good_connection.get.return_value.data_xml = "<data/>"
        session = NETCONFSession(connection=failed_connection, **NETCONF_KWARGS)

        with patch(
            "netmagic.sessions.netconf.manager.connect", return_value=good_connection
        ) as connect:
            response = session.get(("subtree", "<filter/>"), max_tries=2)

        self.assertIsInstance(response, NETCONFResponse)
        self.assertTrue(response.success)
        self.assertEqual(response.response, "<data/>")
        self.assertEqual(response.retries, 2)
        connect.assert_called_once()
        good_connection.get.assert_called_once_with(filter=("subtree", "<filter/>"))

    def test_get_does_not_retry_rpc_errors(self):
        connection = Mock(connected=True)
        error = RPCError(
            to_ele(
                """<rpc-error xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <error-type>application</error-type>
                <error-tag>invalid-value</error-tag>
                <error-severity>error</error-severity>
                </rpc-error>"""
            )
        )
        connection.get.side_effect = error
        session = NETCONFSession(connection=connection, **NETCONF_KWARGS)

        response = session.get(max_tries=3)

        self.assertFalse(response.success)
        self.assertIs(response.response, error)
        self.assertEqual(response.retries, 1)
        connection.get.assert_called_once_with(filter=None)

    def test_get_retries_rpc_timeouts(self):
        connection = Mock(connected=True)
        reply = Mock(data_xml="<data/>")
        connection.get.side_effect = [TimeoutExpiredError(), reply]
        session = NETCONFSession(connection=connection, **NETCONF_KWARGS)

        response = session.get(max_tries=2)

        self.assertTrue(response.success)
        self.assertEqual(response.retries, 2)
        self.assertEqual(connection.get.call_count, 2)
