# -*- encoding: utf-8 -*-
import os
from unittest import TestCase

import pyspark
from pyspark.sql import SparkSession

from ..sparkmlpipe import SparkMLPipe
from ..utils.constants import APP_PATH, CONFIG_RF_REGRESSOR_TEMPLATE_DIR, CONFIG_HANGYAN_FILE


class TestMLPipe(TestCase):

    spark = SparkSession.builder \
        .master("local") \
        .appName("Test") \
        .getOrCreate()

    def test_rf_regressor_hangyan_instantiate(self):
        template_conf_dir = os.path.join(APP_PATH, CONFIG_RF_REGRESSOR_TEMPLATE_DIR)
        data_conf_path = os.path.join(APP_PATH, CONFIG_HANGYAN_FILE)

        instantiated_main_conf, instantiated_stage_conf_list, _ = SparkMLPipe.instantiate(template_conf_dir, data_conf_path)

        self.assertTrue(len(instantiated_stage_conf_list) == 4)

    def test_rf_regressor_hangyan_instantiate_fit(self):
        template_conf_dir = os.path.join(APP_PATH, CONFIG_RF_REGRESSOR_TEMPLATE_DIR)
        data_conf_path = os.path.join(APP_PATH, CONFIG_HANGYAN_FILE)

        model, metrics, feat_importance = SparkMLPipe.instantiate_fit(template_conf_dir, data_conf_path, self.spark)

        self.assertTrue(len(model.stages) == 4)
        self.assertTrue(len(metrics) == 3)
        self.assertTrue(isinstance(feat_importance, pyspark.ml.linalg.SparseVector))
