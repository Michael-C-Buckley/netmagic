"""
NetMagic Network Device Test
"""

# Python Modules
from typing import TYPE_CHECKING
from unittest import TestCase, main
from unittest.mock import Mock, patch

# Local Modules
from netmagic.devices.network_device import NetworkDevice
from netmagic.sessions.terminal import TerminalSession, Session

from tests.classes.common import MockTerminalSession, TestResponse, SSH_KWARGS

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
    command_path = 'netmagic.sessions.terminal.TerminalSession.command'
    hostname_response = TestResponse('hostname TEST HOSTNAME')

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
        self.ssh_session = TerminalSession(**SSH_KWARGS)
        self.device = NetworkDevice(self.ssh_session)
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_creation(self):
        """
        Simple test to ensure the device was properly created and returned
        """
        self.assertIsInstance(self.device, NetworkDevice)
        self.assertIsInstance(self.device.cli_session, TerminalSession)
        self.assertEqual(self.device.hostname, 'TEST HOSTNAME')

    @patch(command_path)
    def test_connect(self, mocked_command):
        """
        Test to ensure the path-through wrapper for the `Session` worked
        """
        result = self.device.connect()
        mocked_command.return_value = self.hostname_response
        # confirm it attempted to connect once
        print(type(self.ssh_session))

if __name__ == '__main__':
    main()