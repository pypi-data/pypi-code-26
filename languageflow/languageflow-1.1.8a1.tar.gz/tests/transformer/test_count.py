# -*- coding: utf-8 -*-
from unittest import TestCase

from languageflow.transformer.count import CountVectorizer


class TestCountVectorizer(TestCase):
    def test_init(self):
        text = ["tôi đi học",
                "tôi ăn cơm",
                "cơm rất ngon"]
        vectorizer = CountVectorizer(ngram_range=(1, 2))
        vectorizer.fit_transform(text)
        vocab = vectorizer.vocabulary_
        self.assertGreater(len(vocab), 5)

    def test_period(self):
        text = [u"tôi đi học",
                u"tôi ăn cơm",
                u"cơm rất ngon"]
        vectorizer = CountVectorizer()
        vectorizer.fit_transform(text)
        self.assertEqual(0, vectorizer.vocabulary_[u"cơm"])
        self.assertEqual(2, vectorizer.period_[0])
