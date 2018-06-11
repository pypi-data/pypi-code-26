# -*- encoding: utf-8 -*-
import os
from unittest import TestCase

import pyspark
from pyspark.sql import SparkSession

from ..sparkmlpipe import SparkMLPipeline
from ..utils.util import load_config
from ..utils.constants import ROOT_PATH, APP_PATH, CONFIG_CLASSIFY_LOG_FILE, CONFIG_CLASSIFY_RF_FILE,\
    CONFIG_REGRESSOR_LINEAR_FILE, CONFIG_REGRESSOR_RF_FILE


class TestPipe(TestCase):

    spark = SparkSession.builder \
        .master("local") \
        .appName("Test") \
        .getOrCreate()

    def test_classify_log_pipe(self):
        conf_path = os.path.join(APP_PATH, CONFIG_CLASSIFY_LOG_FILE)
        config = load_config(conf_path)

        data_path = config['data']['location']

        data = self.spark.read.option('header', 'true')\
            .option("inferSchema", "true") \
            .csv(os.path.join(ROOT_PATH, data_path))

        sparkml_pipe = SparkMLPipeline(config)

        model, y_true, y_pred, _ = sparkml_pipe.fit_with_outputs(data)

        metrics = sparkml_pipe.get_metrics(y_true, y_pred)

        self.assertTrue(len(model.stages) == 9)
        self.assertTrue(len(y_true) == len(y_pred))
        self.assertTrue(len(metrics) == 4)

    def test_classify_rf_pipe(self):
        conf_path = os.path.join(APP_PATH, CONFIG_CLASSIFY_RF_FILE)
        config = load_config(conf_path)

        data_path = config['data']['location']

        data = self.spark.read.option('header', 'true')\
            .option("inferSchema", "true") \
            .csv(os.path.join(ROOT_PATH, data_path))

        sparkml_pipe = SparkMLPipeline(config)

        model, y_true, y_pred, feature_importances = sparkml_pipe.fit_with_outputs(data)

        metrics = sparkml_pipe.get_metrics(y_true, y_pred)

        self.assertTrue(len(model.stages) == 10)
        self.assertTrue(len(y_true) == len(y_pred))
        self.assertTrue(len(metrics) == 4)
        self.assertTrue(isinstance(feature_importances, pyspark.ml.linalg.SparseVector))

    def test_regressor_linear_pipe(self):
        conf_path = os.path.join(APP_PATH, CONFIG_REGRESSOR_LINEAR_FILE)
        config = load_config(conf_path)

        data_path = config['data']['location']

        data = self.spark.read.option('header', 'true')\
            .option("inferSchema", "true") \
            .csv(os.path.join(ROOT_PATH, data_path))

        sparkml_pipe = SparkMLPipeline(config)

        model, y_true, y_pred, _ = sparkml_pipe.fit_with_outputs(data)

        metrics = sparkml_pipe.get_metrics(y_true, y_pred)

        self.assertTrue(len(model.stages) == 9)
        self.assertTrue(len(y_true) == len(y_pred))
        self.assertTrue(len(metrics) == 3)

    def test_regressor_rf_pipe(self):
        conf_path = os.path.join(APP_PATH, CONFIG_REGRESSOR_RF_FILE)
        config = load_config(conf_path)

        data_path = config['data']['location']

        data = self.spark.read.option('header', 'true')\
            .option("inferSchema", "true") \
            .csv(os.path.join(ROOT_PATH, data_path))

        sparkml_pipe = SparkMLPipeline(config)

        model, y_true, y_pred, feature_importances = sparkml_pipe.fit_with_outputs(data)

        metrics = sparkml_pipe.get_metrics(y_true, y_pred)

        self.assertTrue(len(model.stages) == 10)
        self.assertTrue(len(y_true) == len(y_pred))
        self.assertTrue(len(metrics) == 3)
        self.assertTrue(isinstance(feature_importances, pyspark.ml.linalg.SparseVector))
