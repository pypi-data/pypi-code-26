# coding: utf-8

from __future__ import absolute_import

from datetime import date, timedelta
import unittest
from mercury import UnbalancedButterfly, ButterflyValueException
from mercury import OptionLeg


class TestUnbalancedButterfly(unittest.TestCase):
    """Butterfly unit test stubs"""

    """
    todo: note: this will be used to check both unbalanced and balanced butterfly trades
    """

    def setUp(self):
        # These legs MUST be valid for UB
        self.first_leg = OptionLeg(**{
            "expiration_date": date(2018, 5, 14),
            "direction": "LONG",
            "type": "PUT",
            "quantity": 1,
            "strike": 2585
        })
        self.mid_leg = OptionLeg(**{
            "expiration_date": date(2018, 5, 14),
            "direction": "SHORT",
            "type": "PUT",
            "quantity": 2,
            "strike": 2610
        })
        self.third_leg = OptionLeg(**{
            "expiration_date": date(2018, 5, 14),
            "direction": "LONG",
            "type": "PUT",
            "quantity": 2,
            "strike": 2635
        })
        # Make sure the legs are ok
        UnbalancedButterfly(first_leg=self.first_leg,
                            mid_leg=self.mid_leg,
                            third_leg=self.third_leg)

    def tearDown(self):
        pass

    def test_ub_direction_error(self):
        self.first_leg.direction = 'LONG'
        self.mid_leg.direction = 'LONG'
        self.third_leg.direction = 'SHORT'
        with self.assertRaises(ButterflyValueException) as ctx:
            UnbalancedButterfly(first_leg=self.first_leg,
                                mid_leg=self.mid_leg,
                                third_leg=self.third_leg)

    def test_ub_direction_error2(self):
        self.first_leg.direction = 'LONG'
        self.mid_leg.direction = 'LONG'
        self.third_leg.direction = 'LONG'
        with self.assertRaises(ButterflyValueException) as ctx:
            UnbalancedButterfly(first_leg=self.first_leg,
                                mid_leg=self.mid_leg,
                                third_leg=self.third_leg)

    def test_ub_strike_error(self):
        self.first_leg.strike = 3
        self.mid_leg.strike = 2
        self.third_leg.strike = 1
        with self.assertRaises(ButterflyValueException) as ctx:
            UnbalancedButterfly(first_leg=self.first_leg,
                                mid_leg=self.mid_leg,
                                third_leg=self.third_leg)

    def test_ub_type_error(self):
        self.first_leg.type = 'PUT'
        self.mid_leg.type = 'CALL'
        self.third_leg.type = 'PUT'
        with self.assertRaises(ButterflyValueException) as ctx:
            UnbalancedButterfly(first_leg=self.first_leg,
                                mid_leg=self.mid_leg,
                                third_leg=self.third_leg)

    def test_ub_exp_date_error(self):
        self.third_leg.expiration_date = self.first_leg.expiration_date + timedelta(days=1)
        with self.assertRaises(ButterflyValueException) as ctx:
            UnbalancedButterfly(first_leg=self.first_leg,
                                mid_leg=self.mid_leg,
                                third_leg=self.third_leg)

    def test_ub_quantity_error(self):
        self.first_leg.quantity = 1
        self.mid_leg.quantity = 1
        self.third_leg.quantity = 1
        with self.assertRaises(ButterflyValueException) as ctx:
            UnbalancedButterfly(first_leg=self.first_leg,
                                mid_leg=self.mid_leg,
                                third_leg=self.third_leg)


if __name__ == '__main__':
    unittest.main()
