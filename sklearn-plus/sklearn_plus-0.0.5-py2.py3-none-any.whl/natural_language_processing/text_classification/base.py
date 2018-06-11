#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import dill

from sklearn.base import BaseEstimator, ClassifierMixin

import numpy as np

import tensorflow as tf
from tensorflow.contrib import learn

from sklearn_plus.utils import const

from sklearn import preprocessing


class Estimator(BaseEstimator, ClassifierMixin):

    def __init__(self, model_dir, model_fn, params):

        self.model_dir = model_dir
        self.model_fn = model_fn
        self.params = params

        if getattr(self.params, 'filter_sizes', None) is None:
            self.params.add_hparam('filter_sizes', [3, 4, 5])

        if getattr(self.params, 'embed_dim', None) is None:
            self.params.add_hparam('embed_dim', 100)

        if getattr(self.params, 'num_filters', None) is None:
            self.params.add_hparam('num_filters', 256)

        if getattr(self.params, 'dropout_keep_prob', None) is None:
            self.params.add_hparam('dropout_keep_prob', 0.5)

        if getattr(self.params, 'l2_lambda', None) is None:
            self.params.add_hparam('l2_lambda', 0.0001)

        if getattr(self.params, 'decay_steps', None) is None:
            self.params.add_hparam('decay_steps', 6000)

        if getattr(self.params, 'decay_rate', None) is None:
            self.params.add_hparam('decay_rate', 0.65)

        if getattr(self.params, 'learning_rate', None) is None:
            self.params.add_hparam('learning_rate', 0.1)

        assert getattr(self.params, 'batch_size', None) is not None
        assert getattr(self.params, 'num_epochs', None) is not None
        assert getattr(self.params, 'max_document_length', None) is not None

        if os.path.isfile(self.model_dir + '/' + const.filename_vocab):
            with open(self.model_dir + '/' + const.filename_vocab) as f:
                self.vocab_processor = dill.loads(f.read())
            self.params.add_hparam(
                'vocab_size',
                len(self.vocab_processor.vocabulary_))
        else:
            self.vocab_processor =\
                learn.preprocessing.VocabularyProcessor(
                    self.params.max_document_length)

        if os.path.isfile(self.model_dir + '/' + const.filename_label):
            with open(self.model_dir + '/' + const.filename_label) as f:
                self.label_processor = dill.loads(f.read())
            self.params.add_hparam(
                'class_num',
                len(self.label_processor.classes_))
        else:
            self.label_processor = preprocessing.LabelEncoder()

        self.classifier = tf.estimator.Estimator(
            model_dir=self.model_dir,
            model_fn=self.model_fn,
            params=self.params)

    def preprocess_x(self, X):
        return np.array(list(self.vocab_processor.transform(X)))

    def preprocess_y(self, y):
        return self.label_processor.transform(y)

    def postprocess_y(self, y):
        return self.label_processor.inverse_transform(y)

    @classmethod
    def construct_input_fn(cls,
                           word_ids,
                           y=None, batch_size=128, num_epochs=1, shuffle=None):
        return tf.estimator.inputs.numpy_input_fn(
            x={const.word_ids: word_ids},
            y=y,
            batch_size=batch_size,
            num_epochs=num_epochs,
            shuffle=shuffle)

    def fit(self, X_train, y_train, X_valid=None, y_valid=None):

        self.vocab_processor.fit(X_train)
        self.params.add_hparam(
            'vocab_size',
            len(self.vocab_processor.vocabulary_))

        self.label_processor.fit(y_train)
        self.params.add_hparam('class_num', len(self.label_processor.classes_))

        self.classifier = tf.estimator.Estimator(
            model_dir=self.model_dir,
            model_fn=self.model_fn,
            params=self.params)

        train_input_fn = self.construct_input_fn(
            word_ids=self.preprocess_x(X_train),
            y=self.preprocess_y(y_train),
            batch_size=self.classifier.params.batch_size,
            num_epochs=self.classifier.params.num_epochs,
            shuffle=True)
        self.classifier.train(train_input_fn)
        if X_valid is not None and y_valid is not None:
            eval_input_fn = self.construct_input_fn(
                word_ids=self.preprocess_x(X_valid),
                y=self.preprocess_y(y_valid),
                shuffle=True)
            self.classifier.evaluate(eval_input_fn)

        with open(self.model_dir + '/' + const.filename_vocab, 'wb') as f:
            f.write(dill.dumps(self.vocab_processor))
        with open(self.model_dir + '/' + const.filename_label, 'wb') as f:
            f.write(dill.dumps(self.label_processor))

    def predict(self, X):
        predict_input_fn = self.construct_input_fn(
            word_ids=self.preprocess_x(X),
            shuffle=False)

        return [self.postprocess_y(p['class'])
                for p in self.classifier.predict(predict_input_fn)]

    def predict_top_n(self, X, n=1):
        predict_input_fn = self.construct_input_fn(
            word_ids=self.preprocess_x(X),
            shuffle=False)

        response = []
        for p in self.classifier.predict(predict_input_fn):
            top_n_idx = p['prob'].argsort()[0-n:][::-1]
            classes = self.postprocess_y(top_n_idx)
            probs = p['prob'][top_n_idx]

            categories = []

            for i in xrange(n):
                item = {}
                item[u'name'] = unicode(classes[i], 'utf8')
                item[u'confidence'] = probs[i]
                categories.append(item)

            response.append({u'categories': categories})
        return response
