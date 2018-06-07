import socket
import time
import re
from logging import Logger

from cloudshell.cli.cli_service import CliService
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.cli.session.session_exceptions import ExpectedSessionException

from cloudshell.firewall.a10.command_templates import configuration


class SystemActions(object):
    def __init__(self, cli_service, logger):
        """System actions

        :param CliService cli_service: config mode cli_service
        :param Logger logger:
        """

        self._cli_service = cli_service
        self._logger = logger

    def copy(self, source, destination, timeout=180):
        """Copy file from device to tftp or vice versa, as well as copying inside devices filesystem

        :param str source: source file
        :param str destination: destination file
        :param int timeout: session timeout
        """

        CommandTemplateExecutor(
            self._cli_service,
            configuration.COPY,
            timeout=timeout,
        ).execute_command(src=source, dst=destination)


class FirmwareActions(object):
    def __init__(self, cli_service, logger):
        """Firmware actions

        :param CliService cli_service: config mode cli_service
        :param Logger logger:
        """

        self._cli_service = cli_service
        self._logger = logger

    def show_version(self):
        """Show system version"""

        return CommandTemplateExecutor(
            self._cli_service,
            configuration.SHOW_VERSION
        ).execute_command()

    def get_boot_location(self):
        """Get boot location for the device

        :rtype str:
        :return: pri or sec
        """

        version = self.show_version()

        location = re.search(r'Booted from Hard Disk (\w+) image', version).group(1)

        return {
            'primary': 'pri',
            'secondary': 'sec',
        }[location]

    def upgrade(self, src_path):
        """Upgrade the device firmware

        :param str src_path: path to firmware
        """

        location = self.get_boot_location()

        CommandTemplateExecutor(
            self._cli_service,
            configuration.UPGRADE,
        ).execute_command(location=location, src_path=src_path)

        try:
            for _ in range(30):
                self._cli_service.send_command('')
                time.sleep(3)
        except (ExpectedSessionException, socket.error):
            self._logger.info('Rebooting the device')

        self._cli_service.reconnect(300)
