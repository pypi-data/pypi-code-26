import re

from cloudshell.devices.flows.action_flows import SaveConfigurationFlow

from cloudshell.firewall.a10.command_actions.system_actions import SystemActions


class A10SaveFlow(SaveConfigurationFlow):

    def execute_flow(self, folder_path, configuration_type, vrf_management_name=None):
        """ Execute flow which save selected file to the provided destination

        :param str folder_path: destination path where file will be saved
        :param str configuration_type: source file, which will be saved running or startup
        :param str vrf_management_name: Virtual Routing and Forwarding Name
        :return: saved configuration file name
        :rtype: str
        """

        self._logger.info('Start saving configuration')

        if not configuration_type.endswith('-config'):
            configuration_type += '-config'

        folder_path = re.sub(r'^local:/+', '', folder_path)

        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as config_session:
            save_action = SystemActions(config_session, self._logger)
            save_action.copy(configuration_type, folder_path)

        self._logger.info('Configuration successfully saved')
