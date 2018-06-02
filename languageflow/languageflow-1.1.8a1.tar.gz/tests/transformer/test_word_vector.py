# -*- coding: utf-8 -*-
from unittest import TestCase
from languageflow.transformer.word_vector import WordVectorTransformer


class TestWordVectorTransformer(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestWordVectorTransformer, self).__init__(*args, **kwargs)
        self.documents_1 = ["đi học rất vui",
                            "tôi ăn cơm",
                            "cơm hôm nay rất ngon"]

    def test_basic(self):
        documents = self.documents_1
        vectorizer = WordVectorTransformer()
        X = vectorizer.fit_transform(documents)
        self.assertEqual([11, 4, 7, 9], X[0])
        self.assertEqual(10, len(vectorizer.vocab))

        test_document = "bánh mì ngon"
        self.assertEqual([[1, 1, 6]], vectorizer.transform([test_document]))

    def test_padding(self):
        documents = self.documents_1
        vectorizer = WordVectorTransformer(padding='max')
        vectorizer.fit_transform(documents)

        test_document = ["đi học rất vui"]
        X = vectorizer.transform(test_document)
        self.assertEqual([11, 4, 7, 9, 0], X[0])

        test_document = ["đi học thực sự rất vui"]
        X = vectorizer.transform(test_document)
        self.assertEqual([11, 4, 1, 1, 7], X[0])
