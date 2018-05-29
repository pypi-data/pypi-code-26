#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `demo classifier` package."""


import unittest




class TestBiClassifier(unittest.TestCase):
    """Tests for `sklearn_plus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_demo(self):
        from sklearn_plus.neural_network.text_classification.binary_classifier import BiClassifier
        import numpy as np
        x_vals = np.concatenate((np.random.normal(-1, 1, 50), np.random.normal(3, 1, 50)))
        y_vals = np.concatenate((np.repeat(0., 50), np.repeat(1., 50)))
        print('data is ready...')

        clf = BiClassifier(summary_dir='/tmp/sklearn_plus_test',
                             checkpoint_dir='/tmp/sklearn_plus_test')
        clf.fit(x_vals, y_vals)
        print(clf.save('/tmp/sklearn_plus_test'))
        print('saved weight: %f' % clf.sess.run(clf.model.b))

        del clf
        print('del model ...')
        clf = BiClassifier()
        clf.load('/tmp/sklearn_plus_test')
        print('loaded weight: %f' % clf.sess.run(clf.model.b))
        assert (clf.predict(-2)) == [1.]
        assert (clf.predict(4)) == [0.]

        del clf
        print('del model ...')
        clf = BiClassifier()
        clf.load('/tmp/sklearn_plus_test', global_step=61)
        print('loaded weight: %f' % clf.sess.run(clf.model.b))
        assert (clf.predict(-2)) == [1.]
        assert (clf.predict(4)) == [0.]
