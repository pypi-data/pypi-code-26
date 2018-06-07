from cloudshell.devices.runners.firmware_runner import FirmwareRunner

from cloudshell.firewall.a10.flows.a10_load_firmware_flow import A10LoadFirmwareFlow


class A10FirmwareRunner(FirmwareRunner):
    @property
    def load_firmware_flow(self):
        return A10LoadFirmwareFlow(self.cli_handler, self._logger)
