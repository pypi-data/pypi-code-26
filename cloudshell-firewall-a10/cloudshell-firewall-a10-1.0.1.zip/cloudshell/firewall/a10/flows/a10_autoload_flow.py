from cloudshell.devices.flows.snmp_action_flows import AutoloadFlow

from cloudshell.firewall.a10.autoload.a10_snmp_autoload import A10SNMPAutoload


class A10SnmpAutoloadFlow(AutoloadFlow):
    def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
        with self._snmp_handler.get_snmp_service() as snpm_service:
            snmp_autoload = A10SNMPAutoload(
                snpm_service, shell_name, shell_type, resource_name, self._logger)
            return snmp_autoload.discover(supported_os)
