from unittest import TestCase
from exoticst.bit import Bit, BITError


class TestBit(TestCase):
    def test_init_empty(self):
        lst = []
        self.assertRaises(BITError, Bit, len(lst))

    def test_init_with_list_empty(self):
        bit = Bit(5)
        lst = []
        self.assertRaises(BITError, bit.init_with_list, lst)

    def test_range_sum(self):
        lst = [1, 5, 10, 100]
        bit = Bit(len(lst) + 1)
        bit.init_with_list(lst)
        elements = [bit.element(j) for j in range(len(lst))]
        self.assertEqual(lst, elements)

    def test_element(self):
        lst = [1, 5, 10, 100]
        bit = Bit(len(lst) + 1)
        bit.init_with_list(lst)
        expected_0_2 = 16
        realised = bit.range_sum(0, 2)
        self.assertEqual(expected_0_2, realised)
