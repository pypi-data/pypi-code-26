import emlid.devices.device


class StubDevice(emlid.devices.device.Device):
    def __init__(self):
        self.sensors_tests_module_path = ".stubtests.stubtests"
        self.package_path = "tests"
        super(StubDevice, self).__init__("test_files/stub.json")

