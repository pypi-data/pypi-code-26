from mock import patch, MagicMock

from cloudshell.firewall.a10.runners.a10_configuration_runner import A10ConfigurationRunner
from tests.firewall.a10.base_test import BaseA10TestCase, CliEmulator, Command, CONFIG_PROMPT


@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch('cloudshell.cli.session.ssh_session.SSHSession._clear_buffer', MagicMock(return_value=''))
class TestSaveConfig(BaseA10TestCase):

    def _setUp(self, attrs=None):
        super(TestSaveConfig, self)._setUp(attrs)
        self.runner = A10ConfigurationRunner(
            self.logger, self.resource_config, self.api, self.cli_handler)

    def setUp(self):
        self._setUp({
            'Backup Location': '',
            'Backup Type': A10ConfigurationRunner.DEFAULT_FILE_SYSTEM,
        })

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_save_anonymous(self, send_mock, recv_mock):
        ftp_server = 'ftp://192.168.122.10'
        configuration_type = 'running'

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command(
                'copy {0}-config {1}/A10-{0}-\d+-\d+'.format(configuration_type, ftp_server),
                'User name []?',
                regexp=True,
            ),
            Command('', 'Password []?'),
            Command(
                '',
                'Do you want to save the remote host information to a profile for later use?'
                '[yes/no]',
            ),
            Command(
                'no',
                '.\nFile copied successfully.\n{}'.format(CONFIG_PROMPT),
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.save(ftp_server, configuration_type)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_save(self, send_mock, recv_mock):
        ftp_server = 'ftp://user:password@192.168.122.10'
        configuration_type = 'running'

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command(
                'copy {0}-config {1}/A10-{0}-\d+-\d+'.format(configuration_type, ftp_server),
                'Do you want to save the remote host information to a profile for later use?'
                '[yes/no]',
                regexp=True,
            ),
            Command(
                'no',
                '.\nFile copied successfully.\n{}'.format(CONFIG_PROMPT),
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.save(ftp_server, configuration_type)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_fail_to_save(self, send_mock, recv_mock):
        ftp_server = 'ftp://user:password@192.168.122.10'
        configuration_type = 'running'

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command(
                'copy {0}-config {1}/A10-{0}-\d+-\d+'.format(configuration_type, ftp_server),
                'Do you want to save the remote host information to a profile for later use?'
                '[yes/no]',
                regexp=True,
            ),
            Command(
                'no',
                '.\nFailed to copy file\n{}'.format(CONFIG_PROMPT),
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.assertRaisesRegexp(
            Exception,
            'Session returned \'Fail to copy a file\'',
            self.runner.save,
            ftp_server,
            configuration_type,
        )

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_save_to_device(self, send_mock, recv_mock):
        path = ''
        configuration_type = 'running'

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command(
                'copy {0}-config A10-{0}-\d+-\d+'.format(configuration_type),
                '.\nFile copied successfully.\n{}'.format(CONFIG_PROMPT),
                regexp=True,
            ),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.save(path, configuration_type)

        emu.check_calls()
