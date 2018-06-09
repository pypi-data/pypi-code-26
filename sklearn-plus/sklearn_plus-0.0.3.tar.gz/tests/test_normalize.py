#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `normalize` package."""


import unittest

from sklearn_plus.preprocessing.text.zh.normalize import Normalizer


class TestNormalizer(unittest.TestCase):
    """Tests for `sklearn_plus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_zh_normalizer(self):
        normalizer = Normalizer()
        assert normalizer.transform(
            [u'详情查看：http://www.ruyi.ai/，或者关注微信公众号“艾如意宝宝”获取更多信息']
        ) == [u'详情查看 http www ruyi ai 或者关注微信公众号 艾如意宝宝 获取更多信息']
