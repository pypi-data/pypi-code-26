import re

from cloudshell.devices.flows.action_flows import RestoreConfigurationFlow

from cloudshell.firewall.a10.command_actions.system_actions import SystemActions
from cloudshell.firewall.a10.helpers.exceptions import A10Exception


class A10RestoreFlow(RestoreConfigurationFlow):

    def execute_flow(self, path, configuration_type, restore_method, vrf_management_name):
        """ Execute flow which restore selected file to the provided destination

        :param str path: the path to the configuration file, including the configuration file name
        :param str restore_method: the restore method to use when restoring the configuration file,
            append and override
        :param str configuration_type: the configuration type to restore, startup or running
        :param str vrf_management_name: Virtual Routing and Forwarding Name
        """

        self._logger.info('Start restoring configuration')

        if not configuration_type.endswith('-config'):
            configuration_type += '-config'

        path = re.sub(r'^local:/+', '', path)

        if restore_method == 'append':
            raise A10Exception('Device doesn\'t support append restore method')

        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as config_session:
            restore_action = SystemActions(config_session, self._logger)
            restore_action.copy(path, configuration_type)

        self._logger.info('Configuration successfully restored')
