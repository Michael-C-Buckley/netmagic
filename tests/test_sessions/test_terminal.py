# NetMagic Terminal Session Tests

# Python Modules
from typing import TYPE_CHECKING
from unittest import TestCase, main
from unittest.mock import patch

if TYPE_CHECKING:
    from unittest.mock import _patcher

# Third-Party Modules
from netmiko import NetmikoAuthenticationException as AuthException

# Local Modules
from netmagic.common import Transport
from netmagic.common.classes import CommandResponse
from netmagic.sessions import TerminalSession

# Test Modules (init corrects path)
import __init__
from tests.classes.common import MockBaseConnection, SSH_KWARGS

TERMINAL_DIR = 'netmagic.sessions.terminal'

class TestTerminal(TestCase):
    """
    Test container for `TerminalSession`
    """
    @classmethod
    def setUpClass(cls) -> None:
        cls.patchers: dict[str, _patcher] = {}
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
        self.terminal = TerminalSession(connection=MockBaseConnection(), **SSH_KWARGS)
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def prepare_connection_mock(self) -> MockBaseConnection:
        mock = MockBaseConnection()
        mock.send_command.return_value = 'command return'
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
            for test_case in [True, False]:
                self.terminal.connection.is_alive.return_value = test_case
                self.assertTrue(self.terminal.check_session())

    # def test_command(self) -> None:
    #     cmd_return = 'command return'
    #     with self.connection_patch():
    #         self.terminal.connection.send_command.return_value = cmd_return
    #         test_cmd = self.terminal.command
    #         # Successful command
    #         self.assertEqual(test_cmd('').response, cmd_return)
    #         # Blind command
    #         self.assertEqual(test_cmd('', blind=True).response, 'Blind: True')

    def test_blind_command(self):
        """
        Command is the largest and primarily useful method of a terminal session
        """
        # test with no connection
        # test blind
        # normal without error
        # normal with error, then works
        # normal with errors until the max_tries

        # patched_command.return_value = f'TEST_HOSTNAME# TEST COMMAND RESULT'
        blind_output = self.terminal.command('something', blind=True)
        self.assertIsInstance(blind_output, CommandResponse)

    def test_command(self):
        """"""
        output = self.terminal.command('something')
        self.assertIsInstance(output, CommandResponse)

        # test a failure then a success


if __name__ == '__main__':
    main()