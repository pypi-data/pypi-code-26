#!/usr/bin/env python3
# -*- coding: utf-8 -*- #

import unittest
from twsecli import twsecli


class TestAlignmentFunction(unittest.TestCase):
  """ TestAlignmentFunction """
  def test_alignment(self):
    self.assertEqual(twsecli.alignment('中文', 4), '中文')
    self.assertEqual(twsecli.alignment('中文', 6), '中文  ')

  def test_alignment_digit(self):
    self.assertEqual(twsecli.alignment('中文1', 6), '中文1 ')
    self.assertEqual(twsecli.alignment('中12', 6), '中12  ')

  def test_alignment_alphabet(self):
    self.assertEqual(twsecli.alignment('中文a', 6), '中文a ')
    self.assertEqual(twsecli.alignment('中ab', 6), '中ab  ')


class TestColoredFunction(unittest.TestCase):
  """ TestColoredFunction """
  def test_colored(self):
    self.assertEqual(twsecli.colored('綠色', 'green'), '\033[1;32m綠色\033[m')
    self.assertEqual(twsecli.colored('紅色', 'red'), '\033[1;31m紅色\033[m')


class TestTWSELIB(unittest.TestCase):
  """ TestTWSELIB """
  def setUp(self):
    self.twse_lib = twsecli.TWSELIB()

  def tearDown(self):
    del self.twse_lib

  def test_get_cookie(self):
    self.assertIsNotNone(self.twse_lib.get_cookie())

  def test_get_stock_key_tse(self):
    self.assertEqual(self.twse_lib.get_stock_key('0050'), 'tse_0050.tw')

  def test_get_stock_key_otc(self):
    self.assertEqual(self.twse_lib.get_stock_key('5425'), 'otc_5425.tw')

  def test_get_stock_info(self):
    keys = ['tse_0050.tw', 'otc_5425.tw']
    self.assertIsNotNone(self.twse_lib.get_stock_info(keys))


if __name__ == '__main__':
  unittest.main()
