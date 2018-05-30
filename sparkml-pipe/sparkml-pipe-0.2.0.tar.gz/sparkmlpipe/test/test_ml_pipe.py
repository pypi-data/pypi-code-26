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

    # def test_rf_regressor_template_hangyan(self):
    #     conf_dir = os.path.join(APP_PATH, CONFIG_RF_REGRESSOR_TEMPLATE_DIR)
    #
    #     pipe = PipelineReader.load(conf_dir)
    #     self.assertEqual(len(pipe.getStages()), 3)
    #
    #     data_path = os.path.join(ROOT_PATH, 'data/hangyan_chinese.csv')
    #     data = self.spark.read.option('header', 'true')\
    #         .option("inferSchema", "true")\
    #         .csv(data_path)
    #
    #     model = pipe.fit(data)
    #     res = model.transform(data)
    #     df = res.select('prediction').toPandas()
    #     self.assertEqual(df.shape[0], 1343)

    def test_rf_regressor_template_hangyan(self):
        template_conf_dir = os.path.join(APP_PATH, CONFIG_RF_REGRESSOR_TEMPLATE_DIR)
        data_conf_path = os.path.join(APP_PATH, CONFIG_HANGYAN_FILE)

        spark_mlpipe = SparkMLPipe(template_conf_dir, data_conf_path)
        model, metrics, feat_importance = spark_mlpipe.fit(self.spark)

        self.assertTrue(len(model.stages) == 4)
        self.assertTrue(len(metrics) == 3)
        self.assertTrue(isinstance(feat_importance, pyspark.ml.linalg.SparseVector))
