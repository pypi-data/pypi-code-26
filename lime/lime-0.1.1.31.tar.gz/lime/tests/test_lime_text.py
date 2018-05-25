import unittest

import sklearn # noqa
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Lasso
from sklearn.metrics import f1_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

import numpy as np

from lime.lime_text import LimeTextExplainer
from lime.lime_text import IndexedCharacters


class TestLimeText(unittest.TestCase):

    def test_lime_text_explainer_good_regressor(self):
        categories = ['alt.atheism', 'soc.religion.christian']
        newsgroups_train = fetch_20newsgroups(subset='train',
                                              categories=categories)
        newsgroups_test = fetch_20newsgroups(subset='test',
                                             categories=categories)
        class_names = ['atheism', 'christian']
        vectorizer = TfidfVectorizer(lowercase=False)
        train_vectors = vectorizer.fit_transform(newsgroups_train.data)
        test_vectors = vectorizer.transform(newsgroups_test.data)
        nb = MultinomialNB(alpha=.01)
        nb.fit(train_vectors, newsgroups_train.target)
        pred = nb.predict(test_vectors)
        f1_score(newsgroups_test.target, pred, average='weighted')
        c = make_pipeline(vectorizer, nb)
        explainer = LimeTextExplainer(class_names=class_names)
        idx = 83
        exp = explainer.explain_instance(newsgroups_test.data[idx],
                                         c.predict_proba, num_features=6)
        self.assertIsNotNone(exp)
        self.assertEqual(6, len(exp.as_list()))

    def test_lime_text_explainer_bad_regressor(self):
        newsgroups_train = fetch_20newsgroups(subset='train')
        newsgroups_test = fetch_20newsgroups(subset='test')
        # making class names shorter
        class_names = [x.split('.')[-1] if 'misc' not in x
                       else '.'.join(x.split('.')[-2:])
                       for x in newsgroups_train.target_names]
        class_names[3] = 'pc.hardware'
        class_names[4] = 'mac.hardware'
        vectorizer = TfidfVectorizer(lowercase=False)
        train_vectors = vectorizer.fit_transform(newsgroups_train.data)
        test_vectors = vectorizer.transform(newsgroups_test.data)
        nb = MultinomialNB(alpha=.01)
        nb.fit(train_vectors, newsgroups_train.target)
        pred = nb.predict(test_vectors)
        f1_score(newsgroups_test.target, pred, average='weighted')
        c = make_pipeline(vectorizer, nb)
        explainer = LimeTextExplainer(class_names=class_names)
        idx = 1340
        with self.assertRaises(TypeError):
            exp = explainer.explain_instance(# noqa:F841
                newsgroups_test.data[idx], c.predict_proba, num_features=6,
                labels=[0, 17], model_regressor=Lasso())

    def test_lime_text_tabular_equal_random_state(self):
        categories = ['alt.atheism', 'soc.religion.christian']
        newsgroups_train = fetch_20newsgroups(subset='train',
                                              categories=categories)
        newsgroups_test = fetch_20newsgroups(subset='test',
                                             categories=categories)
        class_names = ['atheism', 'christian']
        vectorizer = TfidfVectorizer(lowercase=False)
        train_vectors = vectorizer.fit_transform(newsgroups_train.data)
        test_vectors = vectorizer.transform(newsgroups_test.data)
        nb = MultinomialNB(alpha=.01)
        nb.fit(train_vectors, newsgroups_train.target)
        pred = nb.predict(test_vectors)
        f1_score(newsgroups_test.target, pred, average='weighted')
        c = make_pipeline(vectorizer, nb)

        explainer = LimeTextExplainer(class_names=class_names, random_state=10)
        exp_1 = explainer.explain_instance(newsgroups_test.data[83],
                                           c.predict_proba, num_features=6)

        explainer = LimeTextExplainer(class_names=class_names, random_state=10)
        exp_2 = explainer.explain_instance(newsgroups_test.data[83],
                                           c.predict_proba, num_features=6)

        self.assertTrue(exp_1.as_map() == exp_2.as_map())

    def test_lime_text_tabular_not_equal_random_state(self):
        categories = ['alt.atheism', 'soc.religion.christian']
        newsgroups_train = fetch_20newsgroups(subset='train',
                                              categories=categories)
        newsgroups_test = fetch_20newsgroups(subset='test',
                                             categories=categories)
        class_names = ['atheism', 'christian']
        vectorizer = TfidfVectorizer(lowercase=False)
        train_vectors = vectorizer.fit_transform(newsgroups_train.data)
        test_vectors = vectorizer.transform(newsgroups_test.data)
        nb = MultinomialNB(alpha=.01)
        nb.fit(train_vectors, newsgroups_train.target)
        pred = nb.predict(test_vectors)
        f1_score(newsgroups_test.target, pred, average='weighted')
        c = make_pipeline(vectorizer, nb)

        explainer = LimeTextExplainer(
            class_names=class_names, random_state=10)
        exp_1 = explainer.explain_instance(newsgroups_test.data[83],
                                           c.predict_proba, num_features=6)

        explainer = LimeTextExplainer(
            class_names=class_names, random_state=20)
        exp_2 = explainer.explain_instance(newsgroups_test.data[83],
                                           c.predict_proba, num_features=6)

        self.assertFalse(exp_1.as_map() == exp_2.as_map())

    def test_indexed_characters_bow(self):
        s = 'Please, take your time'
        inverse_vocab = ['P', 'l', 'e', 'a', 's', ',', ' ', 't', 'k', 'y', 'o', 'u', 'r', 'i', 'm']
        positions = [[0], [1], [2, 5, 11, 21], [3, 9],
                     [4], [6], [7, 12, 17], [8, 18], [10],
                     [13], [14], [15], [16], [19], [20]]
        ic = IndexedCharacters(s)

        self.assertTrue(np.array_equal(ic.as_np, np.array(list(s))))
        self.assertTrue(np.array_equal(ic.string_start, np.arange(len(s))))
        self.assertTrue(ic.inverse_vocab == inverse_vocab)
        self.assertTrue(ic.positions == positions)

    def test_indexed_characters_not_bow(self):
        s = 'Please, take your time'

        ic = IndexedCharacters(s, bow=False)

        self.assertTrue(np.array_equal(ic.as_np, np.array(list(s))))
        self.assertTrue(np.array_equal(ic.string_start, np.arange(len(s))))
        self.assertTrue(ic.inverse_vocab == list(s))
        self.assertTrue(np.array_equal(ic.positions, np.arange(len(s))))


if __name__ == '__main__':
    unittest.main()
