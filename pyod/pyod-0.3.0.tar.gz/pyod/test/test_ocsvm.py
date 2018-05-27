import os, sys

# temporary solution for relative imports in case pyod is not installed
# if pyod is installed, no need to use the following line
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_greater
from sklearn.utils.testing import assert_greater_equal
from sklearn.utils.testing import assert_less_equal
from sklearn.metrics import roc_auc_score

from pyod.models.ocsvm import OCSVM
from pyod.utils.load_data import generate_data


class TestOCSVM(unittest.TestCase):
    def setUp(self):
        self.n_train = 100
        self.n_test = 50
        self.contamination = 0.1
        self.roc_floor = 0.6
        self.X_train, self.y_train, _, self.X_test, self.y_test, _ = generate_data(
            n_train=self.n_train, n_test=self.n_test,
            contamination=self.contamination)

        self.clf = clf = OCSVM()
        self.clf.fit(self.X_train)

    def test_parameters(self):
        if not hasattr(self.clf,
                       'decision_scores') or self.clf.decision_scores is None:
            self.assertRaises(AttributeError, 'decision_scores is not set')
        if not hasattr(self.clf, 'y_pred') or self.clf.y_pred is None:
            self.assertRaises(AttributeError, 'y_pred is not set')
        if not hasattr(self.clf, 'threshold_') or self.clf.threshold_ is None:
            self.assertRaises(AttributeError, 'threshold_ is not set')
        if not hasattr(self.clf,
                       'support_') or self.clf.support_ is None:
            self.assertRaises(AttributeError, 'support_ is not set')
        if not hasattr(self.clf,
                       'support_vectors_') or self.clf.support_vectors_ is None:
            self.assertRaises(AttributeError, 'support_vectors_ is not set')
        if not hasattr(self.clf, 'dual_coef_') or self.clf.dual_coef_ is None:
            self.assertRaises(AttributeError, 'dual_coef_ is not set')

        # only available for linear kernel
        # if not hasattr(self.clf, 'coef_') or self.clf.coef_ is None:
        #     self.assertRaises(AttributeError, 'coef_ is not set')
        if not hasattr(self.clf, 'intercept_') or self.clf.intercept_ is None:
            self.assertRaises(AttributeError, 'intercept_ is not set')

    def test_train_scores(self):
        assert_equal(len(self.clf.decision_scores), self.X_train.shape[0])

    def test_prediction_scores(self):
        pred_scores = self.clf.decision_function(self.X_test)

        # check score shapes
        assert_equal(pred_scores.shape[0], self.X_test.shape[0])

        # check performance
        assert_greater(roc_auc_score(self.y_test, pred_scores), self.roc_floor)

    def test_prediction_labels(self):
        pred_labels = self.clf.predict(self.X_test)
        assert_equal(pred_labels.shape, self.y_test.shape)

    def test_prediction_proba(self):
        pred_proba = self.clf.predict_proba(self.X_test)
        assert_greater_equal(pred_proba.min(), 0)
        assert_less_equal(pred_proba.max(), 1)

    def test_prediction_proba(self):
        pred_proba = self.clf.predict_proba(self.X_test)
        assert_greater_equal(pred_proba.min(), 0)
        assert_less_equal(pred_proba.max(), 1)

    def test_fit_predict(self):
        pred_labels = self.clf.fit_predict(self.X_train)
        assert_equal(pred_labels.shape, self.y_train.shape)

    def test_evaluate(self):
        self.clf.evaluate(self.X_test, self.y_test)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
