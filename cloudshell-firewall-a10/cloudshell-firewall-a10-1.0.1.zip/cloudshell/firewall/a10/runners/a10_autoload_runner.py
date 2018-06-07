from cloudshell.devices.runners.autoload_runner import AutoloadRunner

from cloudshell.firewall.a10.flows.a10_autoload_flow import A10SnmpAutoloadFlow


class A10AutoloadRunner(AutoloadRunner):
    def __init__(self, resource_config, logger, snmp_handler):
        super(A10AutoloadRunner, self).__init__(resource_config)
        self._logger = logger
        self.snmp_handler = snmp_handler

    @property
    def autoload_flow(self):
        return A10SnmpAutoloadFlow(self.snmp_handler, self._logger)
