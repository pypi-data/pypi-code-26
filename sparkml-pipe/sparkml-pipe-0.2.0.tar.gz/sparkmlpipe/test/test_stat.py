# -*- encoding: utf-8 -*-
import os
from unittest import TestCase

import pyspark
from pyspark.sql import SparkSession


from ..sparkmlpipe import SparkStatPipeline
from ..utils.util import load_config
from ..utils.constants import ROOT_PATH, APP_PATH, CONFIG_CORR_FILE, CONFIG_CORR_HANGYAN_FILE


class TestStat(TestCase):

    spark = SparkSession.builder \
        .master("local") \
        .appName("Test") \
        .getOrCreate()

    def test_corr_iris(self):
        conf_path = os.path.join(APP_PATH, CONFIG_CORR_FILE)
        config = load_config(conf_path)

        data_path = config['data']['location']

        data = self.spark.read.option('header', 'true') \
            .option("inferSchema", "true") \
            .csv(os.path.join(ROOT_PATH, data_path))

        spark_stat_pipe = SparkStatPipeline(config, data)

        corr = spark_stat_pipe.get_stat()

        self.assertTrue(isinstance(corr, pyspark.ml.linalg.DenseMatrix))

    def test_corr_hangyan(self):
        conf_path = os.path.join(APP_PATH, CONFIG_CORR_HANGYAN_FILE)
        config = load_config(conf_path)

        data_path = config['data']['location']

        data = self.spark.read.option('header', 'true') \
            .option("inferSchema", "true") \
            .csv(os.path.join(ROOT_PATH, data_path))

        spark_stat_pipe = SparkStatPipeline(config, data)

        corr = spark_stat_pipe.get_stat()

        self.assertTrue(isinstance(corr, pyspark.ml.linalg.DenseMatrix))