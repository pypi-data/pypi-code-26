import os
import unittest
import json
import datetime

import asf_granule_util as gu


class TestSentinelGranule(unittest.TestCase):
    def setUp(self):
        self.data_path = os.path.join(
            os.path.dirname(__file__), 'data'
        )

        test_granules_path = os.path.join(self.data_path, 'granules.json')
        with open(test_granules_path, 'r') as f:
            self.ga, self.gb = json.load(f)

        self.ga_obj = gu.SentinelGranule(self.ga)
        self.gb_obj = gu.SentinelGranule(self.gb)

    def test_is_valid(self):
        self.assertTrue(gu.SentinelGranule.is_valid(self.ga))
        self.assertFalse(gu.SentinelGranule.is_valid('bob'))

    def test_matches_granules(self):
        to_str_value = str(self.ga_obj)

        self.assertEqual(to_str_value, self.ga)

    def test_too_short_granules(self):
        too_short_str = 'afosd=b90'

        self.invalid_granules_raise_with(too_short_str)

    def test_invald_mission(self):
        bad_mission = self.gb.replace('B', 'C')

        self.invalid_granules_raise_with(bad_mission)

    def invalid_granules_raise_with(self, test_str):
        with self.assertRaises(gu.InvalidGranuleException):
            gu.SentinelGranule(test_str)

    def test_datetime_objects(self):
        start_date = datetime.datetime(
            year=2015, month=8, day=29, hour=12, minute=37, second=51
        )
        stop_date = datetime.datetime(
            year=2015, month=8, day=29, hour=12, minute=38, second=21
        )

        self.assertEqual(
            start_date,
            self.ga_obj.get_start_date()
        )
        self.assertEqual(
            stop_date,
            self.ga_obj.get_stop_date()
        )

    def test_date_strings(self):
        start_date, stop_date = self.ga[17:25], self.ga[33:41]

        self.assertEqual(start_date, self.ga_obj.start_date)
        self.assertEqual(stop_date, self.ga_obj.stop_date)

    def test_time_strings(self):
        start_time, stop_time = self.ga[26:32], self.ga[42:48]

        self.assertEqual(start_time, self.ga_obj.start_time)
        self.assertEqual(stop_time, self.ga_obj.stop_time)

    def test_str_and_repr(self):
        path = os.path.join(self.data_path, 'correct_prints.json')
        with open(path, 'r') as f:
            correct = json.load(f)['sentinel']

        self.assertEqual(
            correct['str'],
            str(self.ga_obj)
        )

        self.assertEqual(
            correct['repr'],
            repr(self.ga_obj)
        )


if __name__ == '__main__':
    unittest.main()
