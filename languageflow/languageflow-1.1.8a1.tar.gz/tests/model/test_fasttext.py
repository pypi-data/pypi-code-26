from unittest import TestCase

from os.path import join, dirname

from languageflow.api import load
from languageflow.model.fasttext import FastTextClassifier


class TestFastText(TestCase):
    def test_fasttext(self):
        clf = FastTextClassifier()
        clf.fit(['x', 'y'], ['a', 'b'])
        self.assertEqual(clf.predict('x'), 'a')
        self.assertEqual(clf.predict(['x', 'y']), ['a', 'b'])

    def test_load(self):
        model = load("FastText",
                     join(dirname(__file__), "fasttext", "model.bin.bin"))
        y = model.predict(["x", "y"])
        self.assertEqual(2, len(y))

    def test_predict_list(self):
        model = load("FastText",
                     join(dirname(__file__), "fasttext", "model.bin.bin"))

        y = model.predict(["x", "y"])
        self.assertEqual(2, len(y))

        y = model.predict("xy")
