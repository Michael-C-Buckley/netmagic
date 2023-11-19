# NetMagic Terminal Session Tests

# Python Modules
from ipaddress import IPv6Address as IPv6
from typing import TYPE_CHECKING
from unittest import TestCase, main
from unittest.mock import Mock, patch, create_autospec

if TYPE_CHECKING:
    from unittest.mock import _patcher

# Third-Party Modules
from netmiko import NetmikoAuthenticationException as AuthException

# Local Modules
from netmagic.common.types import Transport
from netmagic.sessions.terminal import TerminalSession

# Test Modules (init corrects path)
import __init__
from tests.netmagic_common import MockBaseConnection

TERMINAL_DIR = 'netmagic.sessions.terminal'

class TestTerminal(TestCase):
    """
    Test container for `TerminalSession`
    """
    @classmethod
    def setUpClass(cls) -> None:
        cls.patchers: dict[str, _patcher] = {}
        # cls.patchers['netmiko_connect'] = patch(f'{TERMINAL_DIR}.netmiko_connect', return_value=MockBaseConnection())
        cls.patchers['sleep'] = patch(f'{TERMINAL_DIR}.sleep', return_value=None)
        
        for patcher in cls.patchers.values():
            patcher.start()

        return super().setUpClass()
    
    @classmethod
    def tearDownClass(cls) -> None:
        for patcher in cls.patchers.values():
            patcher.stop()
        return super().tearDownClass()

    def setUp(self) -> None:
        
        connect_kwargs = {
            'host': IPv6('::1'),
            'port': 22,
            'username': 'admin',
            'password': 'admin',
            'secret': 'admin',
            'transport': Transport.SSH,
            'device_type': 'generic_termserver',
            'connection': MockBaseConnection(),
            # Random connection kwarg
            'test': 'test'
        }
        self.terminal = TerminalSession(**connect_kwargs)
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def prepare_connection_mock(self) -> MockBaseConnection:
        mock = MockBaseConnection()
        mock.send_commmand.return_value = 'command return'
        return mock

    def connection_patch(self, dir: str = 'netmiko_connect', return_value = None) -> '_patcher':
        if return_value is None:
            return_value = self.prepare_connection_mock()
        patcher = patch(f'{TERMINAL_DIR}.{dir}', return_value=return_value)
        return patcher
    
    def test_connect(self) -> None:
        # Test the initial connection
        with self.connection_patch() as patcher:
            self.terminal.connection = None

            # No original connection tests a normal successful connect and also test connection args
            self.assertIsNone(self.terminal.connection)
            self.assertTrue(self.terminal.connect(1, 'a', 'a', {'a': 'a'}))
            self.assertIsInstance(self.terminal.connection, MockBaseConnection)

            # Re-testing the early return on connect when an active session already exists
            self.assertTrue(self.terminal.connect())

            # Test the fail-through conditions
            patcher.side_effect = AuthException
            self.terminal.connection = None
            self.assertFalse(self.terminal.connect(3))

        # Test serial connection
        with self.connection_patch('serial_connect'):
            self.terminal.connection = None
            self.terminal.transport = Transport.SERIAL
            self.assertTrue(self.terminal.connect())
            self.assertIsInstance(self.terminal.connection, MockBaseConnection)

    def test_disconnect(self) -> None:
        self.terminal.disconnect()
        self.assertIsNone(self.terminal.connection)

    def test_check_session(self) -> None:
        with self.connection_patch():
            self.assertTrue(self.terminal.check_session())
            self.terminal.connection.is_alive.return_value = False
            self.assertTrue(self.terminal.check_session())

    def test_command(self) -> None:
        cmd_return = 'command return'
        with self.connection_patch():
            self.terminal.connection.send_command.return_value = cmd_return
            test_cmd = self.terminal.command
            # Successful command
            self.assertEqual(test_cmd('').response, cmd_return)
            # Blind command
            self.assertEqual(test_cmd('', blind=True).response, 'Blind: True')



if __name__ == '__main__':
    main()