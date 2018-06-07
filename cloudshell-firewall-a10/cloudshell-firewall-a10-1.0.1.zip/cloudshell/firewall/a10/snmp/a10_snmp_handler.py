from cloudshell.devices.snmp_handler import SnmpHandler

from cloudshell.firewall.a10.flows.a10_disable_snmp_flow import A10DisableSnmpFlow
from cloudshell.firewall.a10.flows.a10_enable_snmp_flow import A10EnableSnmpFlow


class A10SnmpHandler(SnmpHandler):
    def __init__(self, resource_config, logger, api, cli_handler):
        super(A10SnmpHandler, self).__init__(resource_config, logger, api)
        self.cli_handler = cli_handler

    def _create_enable_flow(self):
        return A10EnableSnmpFlow(self.cli_handler, self._logger)

    def _create_disable_flow(self):
        return A10DisableSnmpFlow(self.cli_handler, self._logger)
