#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `jieba_tokenizer` package."""

import unittest
import numpy as np

from sklearn_plus.preprocessing.bag_of_words import TextToBagVec


class TestJiebaTokenizer(unittest.TestCase):
    """Tests for `sklearn_plus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_basic(self):
        tokenizer = TextToBagVec()
        print(tokenizer.fit_transform([u'今天 上海 的 天气', u'今天 上海 天气 不错 吧']))
        assert (tokenizer.fit_transform([u'今天 上海 的 天气', u'今天 上海 天气 不错 吧']) == np.array(
            [[1, 2, 3, 4, 0], [1, 2, 4, 5, 6]])).any()

    def test_hyparameters(self):
        tokenizer = TextToBagVec(max_length=4, min_frequency=2)
        assert (tokenizer.fit_transform([u'今天 上海 的 天气', u'今天 上海 天气 不错 吧']) == np.array(
            [[2, 1, 0, 3], [2, 1, 3, 0]])).any()

