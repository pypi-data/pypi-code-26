# -*- encoding: utf-8 -*-
import os
from unittest import TestCase

import pyspark
from pyspark.sql import SparkSession

from ..utils import util
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

        main_conf_path = os.path.join(template_conf_dir, "main.yaml")
        main_conf = util.load_config(main_conf_path)

        stage_conf_dir = os.path.join(template_conf_dir, "stages/")

        stage_conf_list = util.load_stage_conf_list(main_conf, stage_conf_dir)
        data_conf = util.load_config(data_conf_path)

        instantiated_main_conf, instantiated_stage_conf_list = SparkMLPipe.instantiate(data_conf, main_conf,
                                                                                       stage_conf_list)

        util.save_instance_configs(instantiated_main_conf, instantiated_stage_conf_list)

        self.assertTrue(len(instantiated_stage_conf_list) == 4)

    def test_rf_regressor_hangyan_instantiate_fit(self):
        template_conf_dir = os.path.join(APP_PATH, CONFIG_RF_REGRESSOR_TEMPLATE_DIR)
        data_conf_path = os.path.join(APP_PATH, CONFIG_HANGYAN_FILE)

        main_conf_path = os.path.join(template_conf_dir, "main.yaml")
        main_conf = util.load_config(main_conf_path)

        stage_conf_dir = os.path.join(template_conf_dir, "stages/")

        stage_conf_list = util.load_stage_conf_list(main_conf, stage_conf_dir)
        data_conf = util.load_config(data_conf_path)

        model, metrics, feat_importance = SparkMLPipe.instantiate_fit(data_conf, main_conf,
                                                                      stage_conf_list, self.spark)

        self.assertTrue(len(model.stages) == 4)
        self.assertTrue(len(metrics) == 3)
        self.assertTrue(isinstance(feat_importance, pyspark.ml.linalg.SparseVector))
