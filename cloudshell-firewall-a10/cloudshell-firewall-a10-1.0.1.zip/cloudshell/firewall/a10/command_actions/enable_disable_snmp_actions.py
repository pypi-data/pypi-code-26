import re

from cloudshell.cli.cli_service import CliService
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor

from cloudshell.firewall.a10.command_templates import enable_disable_snmp


class EnableDisableSnmpV2Actions(object):
    USER = 'quali_user'

    def __init__(self, cli_service, logger, community):
        """Enable Disable Snmp actions

        :param CliService cli_service: config mode cli service
        :param logger:
        :param str community: community string
        """

        self._cli_service = cli_service
        self._logger = logger
        self.community = community

    def enable_snmp_server(self):
        """Enable SNMP server"""

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.ENABLE_SNMP_SERVER,
        ).execute_command()

    def enable_snmp(self):
        """Enable snmp on the device"""

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.SNMP_V2_CREATE_REMOVE_USER,
        ).execute_command(user=self.USER)
        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.SNMP_V2_CREATE_COMMUNITY,
        ).execute_command(community=self.community)
        CommandTemplateExecutor(self._cli_service, enable_disable_snmp.EXIT_MODE).execute_command()

    def disable_snmp(self):
        """Disable snmp on the device"""

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.SNMP_V2_CREATE_REMOVE_USER,
        ).execute_command(user=self.USER, remove='')


class EnableDisableSnmpV3Actions(object):
    VIEW = 'quali_view'
    GROUP = 'quali_group'

    def __init__(self, cli_service, logger, user, auth_type, priv_type, password,
                 priv_key):
        """Enable Disable Snmp actions

        :param CliService cli_service: config mode cli service
        :param logger:
        :param str user: user name
        :param str auth_type:
        :param str priv_type:
        :param str password:
        :param str priv_key:
        """

        self._cli_service = cli_service
        self._logger = logger
        self.user = user
        self.auth_type = auth_type
        self.priv_type = priv_type
        self.password = password
        self.priv_key = priv_key

    def get_config(self):
        """Get SNMP config"""

        return CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.SNMP_GET_CONFIG,
        ).execute_command()

    def is_user_exists(self):
        """Check that user exists"""

        pattern = re.compile(
            r'^snmp-server SNMPv3 user {} group .+'.format(re.escape(self.user)),
            re.MULTILINE,
        )
        return bool(pattern.search(self.get_config()))

    def enable_snmp_server(self):
        """Enable SNMP server"""

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.ENABLE_SNMP_SERVER,
        ).execute_command()

    def __create_remove_view(self, remove=False):
        kwargs = {'view': self.VIEW}
        if remove:
            kwargs['remove'] = ''

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.SNMP_V3_CREATE_REMOVE_VIEW,
        ).execute_command(**kwargs)

    def create_view(self):
        """Create SNMP view"""

        self.__create_remove_view()

    def remove_view(self):
        """Remove SNMP view"""

        self.__create_remove_view(remove=True)

    @property
    def security_level(self):

        auth = self.auth_type != 'No Authentication Protocol'
        priv = self.priv_type != 'No Privacy Protocol'

        return {
            (False, False): 'noauth',
            (True, False): 'auth',
            (False, True): 'priv',
            (True, True): 'priv',
        }[auth, priv]

    def __create_remove_group(self, remove=False):
        kwargs = {
            'group': self.GROUP,
            'view': self.VIEW,
            'security_level': self.security_level,
        }
        if remove:
            kwargs['remove'] = ''

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.SNMP_V3_CREATE_REMOVE_GROUP,
        ).execute_command(**kwargs)

    def create_group(self):
        """Create SNMP group"""

        self.__create_remove_group()

    def remove_group(self):
        """Remove SNMP group"""

        self.__create_remove_group(remove=True)

    def __create_remove_snmp_user(self, remove=False):
        kwargs = {
            'user': self.user,
            'group': self.GROUP,
        }
        if remove:
            kwargs['remove'] = ''
        if self.security_level == 'noauth':
            kwargs['no_security'] = ''
        else:
            kwargs['auth_type'] = self.auth_type.lower()
            kwargs['password'] = self.password

            if self.security_level == 'priv':
                kwargs['priv_type'] = 'aes' if 'aes' in self.priv_type.lower() else 'des'
                kwargs['priv_key'] = self.priv_key

        CommandTemplateExecutor(
            self._cli_service,
            enable_disable_snmp.SNMP_V3_CREATE_REMOVE_USER,
        ).execute_command(**kwargs)

    def create_snmp_user(self):
        """Enable snmp user"""

        self.__create_remove_snmp_user()

    def remove_snmp_user(self):
        """Remove snmp user"""

        self.__create_remove_snmp_user(remove=True)
