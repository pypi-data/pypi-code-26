from cloudshell.devices.flows.action_flows import LoadFirmwareFlow

from cloudshell.firewall.a10.command_actions.system_actions import FirmwareActions


class A10LoadFirmwareFlow(LoadFirmwareFlow):

    def execute_flow(self, path, vrf, timeout):
        """Load a firmware onto the device

        :param str path: The path to the firmware file, including the firmware file name
        :param str vrf: Virtual Routing and Forwarding Name
        :param int timeout:
        """

        self._logger.info('Start loading firmware')

        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as config_session:
            firmware_action = FirmwareActions(config_session, self._logger)
            firmware_action.upgrade(path)

        self._logger.info('Firmware updated')
