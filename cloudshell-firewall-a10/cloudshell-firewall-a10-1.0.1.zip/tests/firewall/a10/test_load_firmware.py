import socket

from mock import patch, MagicMock

from cloudshell.firewall.a10.runners.a10_firmware_runner import A10FirmwareRunner
from tests.firewall.a10.base_test import BaseA10TestCase, CliEmulator, Command, CONFIG_PROMPT, \
    ENABLE_PROMPT, LOADING_PROMPT, DEFAULT_PROMPT, ENABLE_PASSWORD


@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch('cloudshell.cli.session.ssh_session.SSHSession._clear_buffer', MagicMock(return_value=''))
@patch('time.sleep', MagicMock())
class TestLoadFirmware(BaseA10TestCase):
    
    def _setUp(self, attrs=None):
        super(TestLoadFirmware, self)._setUp(attrs)
        self.runner = A10FirmwareRunner(self.logger, self.cli_handler)

    def setUp(self):
        self._setUp()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_load_firmware(self, send_mock, recv_mock):
        user = 'user'
        password = 'password'
        path = 'ftp://{}:{}@192.168.122.10/ACOS_non_FTA_4_1_4_332.64.upg'.format(user, password)

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command(
                'show version',
                'Thunder Series Unified Application Service Gateway vThunder\n'
                'Copyright 2007-2017 by A10 Networks, Inc.  All A10 Networks products are\n'
                'protected by one or more of the following US patents:\n'
                '...\n'
                '64-bit Advanced Core OS (ACOS) version 4.1.0-P10, build 105 (Oct-30-2017,17:16)\n'
                'Booted from Hard Disk primary image\n'
                '...\n'
                '{}'.format(CONFIG_PROMPT),
            ),
            Command(
                'upgrade hd pri {} reboot-after-upgrade'.format(path),
                'Getting upgrade package ...\n'
                '.... Done (0 minutes 5 seconds)\n'
                'Decrypt upgrade package ...\n'
                '................. Done (0 minutes 18 seconds)\n'
                'Expand the upgrade package now ...\n'
                '..... Done (0 minutes 6 seconds)\n'
                'Upgrade ...\n'
                '.................................. Upgrade was successful (1 minutes 17 seconds)\n'
                'Rebooting system ...\n'
                '{}'.format(CONFIG_PROMPT),
            ),
            Command('', CONFIG_PROMPT),
            Command('', CONFIG_PROMPT),
            Command('', socket.error()),
            Command('', LOADING_PROMPT),
            Command('', LOADING_PROMPT),
            Command('', LOADING_PROMPT),
            Command('', DEFAULT_PROMPT),
            Command('enable', 'Password'),
            Command(ENABLE_PASSWORD, ENABLE_PROMPT),
            Command('terminal length 0', ENABLE_PROMPT),
            Command('terminal width 300', ENABLE_PROMPT),
            Command('configure', CONFIG_PROMPT),
            Command('logging console disable', CONFIG_PROMPT),
            Command('exit', ENABLE_PROMPT),
            Command('', ENABLE_PROMPT),
            Command('configure', CONFIG_PROMPT),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.load_firmware(path)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_load_firmware_secondary_image(self, send_mock, recv_mock):
        user = 'user'
        password = 'password'
        path = 'ftp://{}:{}@192.168.122.10/ACOS_non_FTA_4_1_4_332.64.upg'.format(user, password)

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command(
                'show version',
                'Thunder Series Unified Application Service Gateway vThunder\n'
                'Copyright 2007-2017 by A10 Networks, Inc.  All A10 Networks products are\n'
                'protected by one or more of the following US patents:\n'
                '...\n'
                '64-bit Advanced Core OS (ACOS) version 4.1.0-P10, build 105 (Oct-30-2017,17:16)\n'
                'Booted from Hard Disk secondary image\n'
                '...\n'
                '{}'.format(CONFIG_PROMPT),
            ),
            Command(
                'upgrade hd sec {} reboot-after-upgrade'.format(path),
                'Getting upgrade package ...\n'
                '.... Done (0 minutes 5 seconds)\n'
                'Decrypt upgrade package ...\n'
                '................. Done (0 minutes 18 seconds)\n'
                'Expand the upgrade package now ...\n'
                '..... Done (0 minutes 6 seconds)\n'
                'Upgrade ...\n'
                '.................................. Upgrade was successful (1 minutes 17 seconds)\n'
                'Rebooting system ...\n'
                '{}'.format(CONFIG_PROMPT),
            ),
            Command('', CONFIG_PROMPT),
            Command('', CONFIG_PROMPT),
            Command('', socket.error()),
            Command('', LOADING_PROMPT),
            Command('', LOADING_PROMPT),
            Command('', LOADING_PROMPT),
            Command('', DEFAULT_PROMPT),
            Command('enable', 'Password'),
            Command(ENABLE_PASSWORD, ENABLE_PROMPT),
            Command('terminal length 0', ENABLE_PROMPT),
            Command('terminal width 300', ENABLE_PROMPT),
            Command('configure', CONFIG_PROMPT),
            Command('logging console disable', CONFIG_PROMPT),
            Command('exit', ENABLE_PROMPT),
            Command('', ENABLE_PROMPT),
            Command('configure', CONFIG_PROMPT),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.load_firmware(path)

        emu.check_calls()

    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_load_firmware_ftp_anonymous(self, send_mock, recv_mock):
        path = 'ftp://192.168.122.10/ACOS_non_FTA_4_1_4_332.64.upg'

        emu = CliEmulator([
            Command('configure', CONFIG_PROMPT),
            Command(
                'show version',
                'Thunder Series Unified Application Service Gateway vThunder\n'
                'Copyright 2007-2017 by A10 Networks, Inc.  All A10 Networks products are\n'
                'protected by one or more of the following US patents:\n'
                '...\n'
                '64-bit Advanced Core OS (ACOS) version 4.1.0-P10, build 105 (Oct-30-2017,17:16)\n'
                'Booted from Hard Disk secondary image\n'
                '...\n'
                '{}'.format(CONFIG_PROMPT),
            ),
            Command(
                'upgrade hd sec {} reboot-after-upgrade'.format(path),
                'Getting upgrade package ...\n'
                '.... Done (0 minutes 5 seconds)\n'
                'Decrypt upgrade package ...\n'
                '................. Done (0 minutes 18 seconds)\n'
                'Expand the upgrade package now ...\n'
                '..... Done (0 minutes 6 seconds)\n'
                'Upgrade ...\n'
                '.................................. Upgrade was successful (1 minutes 17 seconds)\n'
                'Rebooting system ...\n'
                '{}'.format(CONFIG_PROMPT),
            ),
            Command('', CONFIG_PROMPT),
            Command('', CONFIG_PROMPT),
            Command('', socket.error()),
            Command('', LOADING_PROMPT),
            Command('', LOADING_PROMPT),
            Command('', LOADING_PROMPT),
            Command('', DEFAULT_PROMPT),
            Command('enable', 'Password'),
            Command(ENABLE_PASSWORD, ENABLE_PROMPT),
            Command('terminal length 0', ENABLE_PROMPT),
            Command('terminal width 300', ENABLE_PROMPT),
            Command('configure', CONFIG_PROMPT),
            Command('logging console disable', CONFIG_PROMPT),
            Command('exit', ENABLE_PROMPT),
            Command('', ENABLE_PROMPT),
            Command('configure', CONFIG_PROMPT),
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.load_firmware(path)

        emu.check_calls()
