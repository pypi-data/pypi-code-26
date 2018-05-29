#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `jieba_tokenizer` package."""


import unittest

from sklearn_plus.preprocessing.text.zh.jieba_tokenizer import JiebaTokenizer


class TestJiebaTokenizer(unittest.TestCase):
    """Tests for `sklearn_plus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_basic(self):
        tokenizer = JiebaTokenizer()
        assert tokenizer.transform([u'今天上海的天气']) == [u'今天 上海 的 天气']

    def test_words(self):
        tokenizer = JiebaTokenizer(words=[u'上海的天气'])
        assert tokenizer.transform([u'今天上海的天气']) == [u'今天 上海的天气']
