import json
import importlib
from emlid.devices.tester import TestDesc, TestCase


class Device:
    sensors_tests_module_path = ".sensortests.sensortests"
    package_path = "emlid.devices"

    def __init__(self, config):
        self.config = config

    def create_test_case(self, case):
        sensortests_module = importlib.import_module(self.sensors_tests_module_path, self.package_path)
        descriptor = TestDesc(cls=getattr(sensortests_module, case["cls"]), args=case["args"])
        test_case = TestCase(name=case["name"], descriptor=descriptor)
        return test_case

    def get_all_tests(self):
        with open(self.config) as conf:
            cases = json.load(conf)

        return map(self.create_test_case, cases)
