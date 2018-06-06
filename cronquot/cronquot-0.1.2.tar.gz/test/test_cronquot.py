import unittest
import os
from cronquot.cronquot import has_directory


class CronquotTest(unittest.TestCase):

    def test_has_directory(self):
        sample_dir = os.path.join(
                os.path.dirname(__file__), 'crontab')
        self.assertTrue(has_directory(sample_dir))

    def test_parse_command(self):
        pass

    def test_is_cron_script(self):
        pass

    def test_normalize_cron_script(self):
        pass

    def test_has_cosistency_in_result(self):
        pass

    def test_simple_cron_pattern(self):
        pass

if __name__ == '__main__':
    unittest.test()
