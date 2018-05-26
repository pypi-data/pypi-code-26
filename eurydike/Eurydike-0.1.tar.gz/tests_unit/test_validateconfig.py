import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pelops.read_config import read_config, validate_config
from eurydike.eventdetectionmanager import EventDetectionManager


class TestValidateConfig(unittest.TestCase):
    def test_validate_config(self):
        config = read_config("config.yaml")
        validation_result = validate_config(config, EventDetectionManager._get_schema())
        self.assertIsNone(validation_result)


if __name__ == '__main__':
    unittest.main()
