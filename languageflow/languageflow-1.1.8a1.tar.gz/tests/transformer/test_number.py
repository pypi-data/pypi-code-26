# -*- coding: utf-8 -*-
from unittest import TestCase
from languageflow.transformer.number import NumberRemover


class TestCountVectorizer(TestCase):
    def test_tfidf(self):
        text = ["tôi đi học 0123",
                "tôi ăn 456 cơm",
                "789 cơm rất ngon"]
        transfomer = NumberRemover()
        actual = transfomer.transform(text)
        expected = ["tôi đi học ",
                    "tôi ăn  cơm",
                    " cơm rất ngon"]
        self.assertEqual(actual, expected)
