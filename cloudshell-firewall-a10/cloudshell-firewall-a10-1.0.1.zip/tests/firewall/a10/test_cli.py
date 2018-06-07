from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession

from cloudshell.firewall.a10.cli.a10_command_modes import DefaultCommandMode, EnableCommandMode, \
    ConfigCommandMode
from tests.firewall.a10.base_test import BaseA10TestCase


class TestA10Cli(BaseA10TestCase):
    def test_default_mode(self):
        self._setUp()
        self.assertIsInstance(self.cli_handler.default_mode, DefaultCommandMode)

    def test_enable_mode(self):
        self._setUp()
        self.assertIsInstance(self.cli_handler.enable_mode, EnableCommandMode)

    def test_config_mode(self):
        self._setUp()
        self.assertIsInstance(self.cli_handler.config_mode, ConfigCommandMode)

    def test_get_ssh_session(self):
        self._setUp({'CLI Connection Type': 'ssh'})
        self.assertIsInstance(self.cli_handler._new_sessions(), SSHSession)

    def test_get_telnet_session(self):
        self._setUp({'CLI Connection Type': 'telnet'})
        self.assertIsInstance(self.cli_handler._new_sessions(), TelnetSession)

    def test_get_sessions_by_default(self):
        self._setUp({'CLI Connection Type': ''})
        sessions = self.cli_handler._new_sessions()
        ssh, telnet = sessions

        self.assertIsInstance(ssh, SSHSession)
        self.assertIsInstance(telnet, TelnetSession)
