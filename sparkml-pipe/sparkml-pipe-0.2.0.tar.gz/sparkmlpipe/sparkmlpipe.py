# -*- encoding: utf-8 -*-
from .utils.pipeline import fit_pipeline, get_pipeline_builder, verify_config, verify_input_dataset
import os

from .utils import util
from .utils import constants

class SparkMLPipeline:
    def __init__(self, config):
        verify_config(config)

        self.config = config

        self.pipe_builder = get_pipeline_builder(config['pipe']['type'])(config)
        self._pipeline, self.label_col = self.pipe_builder.build_pipeline()

    def fit(self, training_data):
        verify_input_dataset(self.config, training_data)
        model = self._pipeline.fit(training_data)

        return model

    def fit_with_outputs(self, training_data):
        verify_input_dataset(self.config, training_data)
        model, y_true, y_pred, feature_importances = \
            fit_pipeline(self._pipeline, self.config, training_data, self.label_col)

        return model, y_true, y_pred, feature_importances

    def get_metrics(self, y_true, y_pred):
        return self.pipe_builder.get_metrics(y_true, y_pred)


class SparkStatPipeline:
    def __init__(self, config, data):
        verify_config(config)
        verify_input_dataset(config, data)

        self.config = config

        pipe_builder = get_pipeline_builder(config['pipe']['type'])
        self._pipeline = pipe_builder(config, data)

    def get_stat(self):
        stat = self._pipeline.compute_stat()

        return stat


class SparkMLPipe:
    def __init__(self, template_conf_dir, data_conf_path):
        self.template_conf_dir = template_conf_dir
        self.template_stage_confs_dir = os.path.join(self.template_conf_dir, "stages")
        self.data_conf = util.load_config(data_conf_path)

        mlpipe_builder_type = util.get_class(self.main_conf['class'])
        self.mlpipe_builder = mlpipe_builder_type()
        self.mlpipe_builder.build(self.template_stage_confs_dir, self.data_conf)

    @property
    def main_conf(self):
        main_conf_path = os.path.join(self.template_conf_dir, "main.yaml")
        return util.load_config(main_conf_path)

    def fit(self, spark):
        data = spark.read.option('header', 'true')\
            .option("inferSchema", "true") \
            .csv(os.path.join(constants.ROOT_PATH, self.data_conf['location']))

        self.mlpipe_builder.fit(data)
        model = self.mlpipe_builder.get_model()
        metrics = self.mlpipe_builder.get_metrics(data)
        feat_importance = self.mlpipe_builder.get_feat_importance()

        return model, metrics, feat_importance
