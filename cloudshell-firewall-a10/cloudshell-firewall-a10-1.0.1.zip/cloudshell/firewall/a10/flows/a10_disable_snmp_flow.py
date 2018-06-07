from logging import Logger

from cloudshell.devices.flows.cli_action_flows import EnableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters, SNMPV2WriteParameters,\
    SNMPV2ReadParameters

from cloudshell.firewall.a10.command_actions.enable_disable_snmp_actions import \
    EnableDisableSnmpV2Actions, EnableDisableSnmpV3Actions
from cloudshell.firewall.a10.helpers.exceptions import A10Exception


class A10DisableSnmpFlow(EnableSnmpFlow):
    def execute_flow(self, snmp_param):
        if isinstance(snmp_param, SNMPV3Parameters):
            Flow = A10DisableSnmpV3
        else:
            Flow = A10DisableSnmpV2

        return Flow(self._cli_handler, self._logger, snmp_param).execute()


class A10DisableSnmpV2(object):
    def __init__(self, cli_handler, logger, snmp_param):
        """Disable SNMP v2

        :param CliHandlerImpl cli_handler:
        :param Logger logger:
        :param SNMPV2WriteParameters|SNMPV2ReadParameters snmp_param:
        """

        self._cli_handler = cli_handler
        self._logger = logger
        self.snmp_param = snmp_param

    def execute(self):
        community = self.snmp_param.snmp_community
        if isinstance(self.snmp_param, SNMPV2WriteParameters):
            raise A10Exception('ACOS devices doesn\'t support write communities')

        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as conf_session:
            self._logger.info('Start removing SNMP community {}'.format(community))

            snmp_actions = EnableDisableSnmpV2Actions(conf_session, self._logger, community)
            snmp_actions.disable_snmp()

            self._logger.info('SNMP community {} removed'.format(community))


class A10DisableSnmpV3(object):
    SNMP_AUTH_MAP = {v: k for k, v in SNMPV3Parameters.AUTH_PROTOCOL_MAP.items()}
    SNMP_PRIV_MAP = {v: k for k, v in SNMPV3Parameters.PRIV_PROTOCOL_MAP.items()}
    EXPECTED_PRIV_TYPES = ('No Privacy Protocol', 'DES', 'AES-128')

    def __init__(self, cli_handler, logger, snmp_param):
        """Disable SNMP v3

        :param CliHandlerImpl cli_handler:
        :param Logger logger:
        :param SNMPV3Parameters snmp_param:
        """

        self._cli_handler = cli_handler
        self._logger = logger
        self.snmp_param = snmp_param

    def execute(self):
        auth_type = self.SNMP_AUTH_MAP[self.snmp_param.auth_protocol]
        priv_type = self.SNMP_PRIV_MAP[self.snmp_param.private_key_protocol]
        user = self.snmp_param.snmp_user

        self._validate_parameters(priv_type)

        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as conf_session:

            snmp_actions = EnableDisableSnmpV3Actions(
                conf_session,
                self._logger,
                self.snmp_param.snmp_user,
                auth_type,
                priv_type,
                self.snmp_param.snmp_password,
                self.snmp_param.snmp_private_key,
            )
            snmp_actions.enable_snmp_server()

            self._logger.info('Start disabling SNMP User {}'.format(user))

            if not snmp_actions.is_user_exists():
                self._logger.info('Already disabled SNMP User {}'.format(user))
                return

            snmp_actions.remove_snmp_user()
            snmp_actions.remove_group()
            snmp_actions.remove_view()

            if snmp_actions.is_user_exists():
                raise A10Exception('Failed to disable SNMP User {}'.format(user))

            self._logger.info('SNMP User {} disabled'.format(user))

    def _validate_parameters(self, priv_type):
        if priv_type not in self.EXPECTED_PRIV_TYPES:
            raise A10Exception('Doen\'t supported private key protocol {}'.format(priv_type))
