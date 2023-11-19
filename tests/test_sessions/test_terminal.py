# NetMagic Terminal Session Tests

# Python Modules
from ipaddress import IPv6Address as IPv6
from typing import TYPE_CHECKING
from unittest import TestCase, main
from unittest.mock import Mock, patch

if TYPE_CHECKING:
    from unittest.mock import _patcher

from netmiko import NetmikoAuthenticationException as AuthException

# Local Modules
from netmagic.common.types import Transport
from netmagic.sessions.terminal import TerminalSession

TERMINAL_DIR = 'netmagic.sessions.terminal'

class TestTerminal(TestCase):
    """
    Test container for `TerminalSession`
    """
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_connect_mock: Mock = Mock()
        cls.patchers: dict[str, _patcher] = {}
        cls.patchers['netmiko_connect'] = patch(f'{TERMINAL_DIR}.netmiko_connect', return_value=cls.base_connect_mock)
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
        self.base_connect_mock.reset_mock()
        connect_kwargs = {
            'host': IPv6('::1'),
            'port': 22,
            'username': 'admin',
            'password': 'admin',
            'secret': 'admin',
            'transport': Transport.SSH,
            'device_type': 'generic_termserver',
            'connection': self.base_connect_mock,
        }
        self.terminal = TerminalSession(**connect_kwargs)
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_connect(self) -> None:
        # Test the initial connection
        with patch(f'{TERMINAL_DIR}.netmiko_connect') as connect_patch:
            connect_patch.return_value = Mock()
            self.terminal.connection = None
            # No original connection tests a normal succesful connect
            self.assertIsNone(self.terminal.connection)
            self.assertTrue(self.terminal.connect())
            self.assertEqual(self.terminal.connection, connect_patch.return_value)

            # Re-testing the early return on connect when an active session already exists
            self.assertTrue(self.terminal.connect())

            # Test the fail-through conditions
            connect_patch.side_effect = lambda **kwargs: (_ for _ in ()).throw(AuthException)
            self.assertFalse(self.terminal.connect(3))

    def test_disconnect(self) -> None:
        self.terminal.connection = Mock()
        self.terminal.disconnect()
        self.assertIsNone(self.terminal.connection)

    def test_check_session(self) -> None:
        func = self.terminal.check_session
        self.assertTrue(func())

        self.terminal.connection.is_alive.return_value = False
        self.assertTrue(self.terminal.check_session())

if __name__ == '__main__':
    main()