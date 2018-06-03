# -*- coding: utf-8 -*-
"""
__title__ = 'SparkStarter'
__author__ = 'JieYuan'
__mtime__ = '2018/3/16'
"""
from __future__ import absolute_import, unicode_literals
import os
from glob import glob

from pyspark.sql import SparkSession


class SparkStarter:
    """.bashrc or .bash_profile
    SPARK_HOME=.../spark
    PYTHON_HOME=.../anaconda3
    PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.10.6-src.zip:$SPARK_HOME/python
    PATH=$PYTHON_HOME/bin:$SPARK_HOME/bin:$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.4-src.zip:$PATH

    # pyspark (jupyter notebook)
    export PYSPARK_PYTHON=python3
    export PYSPARK_DRIVER_PYTHON=ipython
    export PYSPARK_DRIVER_PYTHON_OPTS="notebook"
    """

    def __init__(self, SPARK_HOME=None, PYSPARK_PYTHON=None):
        assert SPARK_HOME is not None
        if PYSPARK_PYTHON:
            os.environ["PYSPARK_PYTHON"] = PYSPARK_PYTHON
        else:
            os.environ["PYSPARK_PYTHON"] = os.popen('which python').read().strip()
        os.environ["SPARK_HOME"] = SPARK_HOME
        os.sys.path.append("%s/python" % SPARK_HOME)
        os.sys.path.append(glob("%s/python/lib/py4j*.zip" % SPARK_HOME)[0])

    @property
    def spark(self):
        spark = SparkSession.builder \
            .appName("iSpark") \
            .config('log4j.rootCategory', "WARN") \
            .enableHiveSupport() \
            .getOrCreate()
        return spark

    @property
    def sc(self):
        return self.spark.sparkContext






















































SPARK = \
    '''
          ____              __
         / __/__  ___ _____/ /__
        _\ \/ _ \/ _ `/ __/  '_/
       /___/ .__/\_,_/_/ /_/\_\    >>>https://pypi.org/project/iSpark
          /_/

    '''
if __name__ == '__main__':
    pass
else:
    print(SPARK)
