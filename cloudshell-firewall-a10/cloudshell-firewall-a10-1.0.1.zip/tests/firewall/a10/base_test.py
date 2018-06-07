import re
from collections import deque
from unittest import TestCase

from cloudshell.devices.driver_helper import get_cli
from cloudshell.devices.standards.firewall.configuration_attributes_structure import \
    create_firewall_resource_from_context
from cloudshell.shell.core.driver_context import ResourceCommandContext, ResourceContextDetails
from mock import create_autospec, MagicMock

from cloudshell.firewall.a10.cli.a10_cli_handler import A10CliHandler as CliHandler

LOADING_PROMPT = 'vThunder(LOADING)>'
DEFAULT_PROMPT = 'vThunder(NOLICENSE)>'
ENABLE_PROMPT = 'vThunder(NOLICENSE)#'
ENABLE_PASSWORD = 'enable_password'
CONFIG_PROMPT = 'vThunder(config)(NOLICENSE)#'


class Command(object):
    def __init__(self, request, response, regexp=False):
        self.request = request
        self.response = response
        self.regexp = regexp

    def __repr__(self):
        return 'Command({!r}, {!r}, {!r})'.format(self.request, self.response, self.regexp)


class CliEmulator(object):
    def __init__(self, commands=None):
        self.request = None

        self.commands = deque([
            Command(None, DEFAULT_PROMPT),
            Command('', DEFAULT_PROMPT),
            Command('enable', 'Password'),
            Command(ENABLE_PASSWORD, ENABLE_PROMPT),
            Command('terminal length 0', ENABLE_PROMPT),
            Command('terminal width 300', ENABLE_PROMPT),
            Command('configure', CONFIG_PROMPT),
            Command('logging console disable', CONFIG_PROMPT),
            Command('exit', ENABLE_PROMPT),
            Command('', ENABLE_PROMPT),
        ])

        if commands:
            self.commands.extend(commands)

    def _get_response(self):
        try:
            command = self.commands.popleft()
        except IndexError:
            raise IndexError('Not expected request "{}"'.format(self.request))

        if not (not command.regexp and command.request == self.request
                or command.regexp and re.search(command.request, self.request)):
            raise KeyError('Unexpected request - "{}"\n'
                           'Expected - "{}"'.format(self.request, command.request))

        if isinstance(command.response, Exception):
            raise command.response
        else:
            return command.response

    def receive_all(self, timeout, logger):
        return self._get_response()

    def send_line(self, command, logger):
        self.request = command

    def check_calls(self):
        if self.commands:
            commands = '\n'.join('\t\t- {}'.format(command.request) for command in self.commands)
            raise ValueError('Not executed commands: \n{}'.format(commands))


class BaseA10TestCase(TestCase):
    SHELL_NAME = ''

    def create_context(self, attrs=None):
        context = create_autospec(ResourceCommandContext)
        context.resource = create_autospec(ResourceContextDetails)
        context.resource.name = 'A10'
        context.resource.fullname = 'A10'
        context.resource.family = 'CS_Firewall'
        context.resource.address = 'host'
        context.resource.attributes = {}

        attributes = {
            'User': 'user',
            'Password': 'password',
            'Enable Password': ENABLE_PASSWORD,
            'host': 'host',
            'CLI Connection Type': 'ssh',
            'Sessions Concurrency Limit': '1',
        }
        attributes.update(attrs or {})

        for key, val in attributes.items():
            context.resource.attributes['{}{}'.format(self.SHELL_NAME, key)] = val

        return context

    @staticmethod
    def _set_snmp_v3_protocols(resource_config, attrs):
        # for now FirewallResource doesn't support auth and priv protocol but we do
        resource_config.snmp_v3_auth_protocol = attrs.get(
            'SNMP V3 Authentication Protocol', 'No Authentication Protocol')
        resource_config.snmp_v3_priv_protocol = attrs.get(
            'SNMP V3 Privacy Protocol', 'No Privacy Protocol')

    def _setUp(self, attrs=None):
        if attrs is None:
            attrs = {}

        self.resource_config = create_firewall_resource_from_context(
            self.SHELL_NAME, ['ACOS'], self.create_context(attrs))
        self._set_snmp_v3_protocols(self.resource_config, attrs)
        self._cli = get_cli(int(self.resource_config.sessions_concurrency_limit))

        self.logger = MagicMock()
        self.api = MagicMock(DecryptPassword=lambda password: MagicMock(Value=password))

        self.cli_handler = CliHandler(self._cli, self.resource_config, self.logger, self.api)

    def tearDown(self):
        self._cli._session_pool._session_manager._existing_sessions = []
