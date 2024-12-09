"""
NetMagic Network Device Test
"""

# Python Modules
from unittest import TestCase, main
from unittest.mock import Mock, patch

# Local Modules
from netmagic.devices.network_device import NetworkDevice
from netmagic.sessions.terminal import TerminalSession


from tests.classes.common import (
    MockBaseConnection, MockTerminalSession, TestResponse, SSH_KWARGS
)

# device creation
# connect/disconnect
# session prep
# CLI enable
# send config

## Loose wrappers
# write mem
# show run
# int status
# lldp

## intentionally not implemented generic
# optics
# media

class TestNetworkDevice(TestCase):
    """
    Test Container for Network Device
    """
    test_hostname = 'TEST_HOSTNAME'
    command_path = 'netmagic.sessions.terminal.TerminalSession.command'
    hostname_response = TestResponse(f'hostname {test_hostname}')


    @classmethod
    def setUpClass(cls) -> None:
        return super().setUpClass()
    
    @classmethod
    def tearDownClass(cls) -> None:
        return super().tearDownClass()
    
    def ssh_command_side_effect(self, *args, **kwargs):
        if args == ('show run | i hostname',):
            return 'TEST NETWORK DEVICE'
    
    @patch(command_path)
    def setUp(self, mocked_command) -> None:
        mocked_command.return_value = self.hostname_response
        self.connection_mock = MockBaseConnection()
        self.ssh_session = TerminalSession(connection=self.connection_mock, **SSH_KWARGS)
        self.device = NetworkDevice(self.ssh_session)
        return super().setUp()
    
    def tearDown(self) -> None:
        self.device = None
        return super().tearDown()
    
    def test_creation(self):
        """
        Simple test to ensure the device was properly created and returned
        """
        self.assertIsInstance(self.device, NetworkDevice)
        self.assertIsInstance(self.device.cli_session, TerminalSession)
        self.assertEqual(self.device.hostname, 'TEST_HOSTNAME')

    @patch(command_path)
    def test_connect(self, mocked_command):
        """
        Test to ensure the path-through wrapper for the `Session` worked
        """
        result = self.device.connect()
        mocked_command.return_value = self.hostname_response
        # confirm it attempted to connect once
        print(type(self.ssh_session))

    def test_disconnect(self):
        """"""
        # Unspecified, all sessions (Spec is acceptable since all share `disconnect` parent method)
        self.device.cli_session = MockTerminalSession()
        self.device.restconf_session = MockTerminalSession()
        self.device.netconf_session = MockTerminalSession()

        self.device.disconnect()

        session_list: list[MockTerminalSession] = [
            self.device.cli_session,
            self.device.netconf_session,
            self.device.restconf_session
        ]

        for session in session_list:
            session.disconnect.assert_called_once()

        # Specified Session, replace and disconnect it alone
        self.device.cli_session = MockTerminalSession()
        self.device.disconnect(self.device.cli_session)
        self.device.cli_session.disconnect.assert_called_once()

    def test_write_memory(self):
        """
        Test for write memory wrapper
        """
        output = self.device.write_memory()
        self.connection_mock.send_command.assert_called_once()

    # Identity and Status Section

    # get_hostname
    # get_running_config
    # get_interface_status
    # get_lldp

    def test_not_implemented(self):
        """
        Explicitly raises an a not implemented error due to no standardized handling
        For `get_media` and `get_optics`, which are overriden by child classes
        """
        for method in [self.device.get_media, self.device.get_optics]:
            with self.assertRaises(NotImplementedError):
                method()

    def test_get_lldp(self):
        """
        LLDP is just a thin wrapper for an unspecified device
        """
        self.device.cli_session = MockTerminalSession()
        output = self.device.get_lldp()
        self.device.cli_session.command.assert_called_once()


if __name__ == '__main__':
    main()