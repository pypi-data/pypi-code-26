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
    @staticmethod
    # def instantiate(template_conf_dir, data_conf_path):
    def instantiate(data_conf, template_main_conf, template_stage_confs):
        """
        Based on the stage_conf_list and data_conf, generate the instantiated_main_conf and instantiated_stage_conf_list
        """
        mlpipe_builder_type = util.get_class(template_main_conf['class'])
        mlpipe_builder = mlpipe_builder_type()

        instantiated_main_conf, instantiated_stage_conf_list, err_msg = mlpipe_builder.instantiate(data_conf,
                                                                                          template_stage_confs)

        if err_msg is not None:
            return None, None, err_msg

        return instantiated_main_conf, instantiated_stage_conf_list, None

    @staticmethod
    # def fit(instantiated_conf_dir, spark):
    def fit(instantiated_main_conf, instantiated_stage_confs, spark, data_host='file://'):
        """
        Based on the instantiated_conf_dir, instantiate and fit the pipeline model
        @:return model Pipeline model
        @:return metrics Pipeline Model evaluation metrics
        @:return feat_importance Model feature importance, can be None
        """
        mlpipe_builder_type = util.get_class(instantiated_main_conf['class'])
        mlpipe_builder = mlpipe_builder_type()

        data = spark.read.option('header', 'true')\
            .option("inferSchema", "true") \
            .csv(os.path.join(data_host, instantiated_main_conf['data']['location']))

        model, metrics, feat_importance, fit_err_msg = \
            mlpipe_builder.fit(instantiated_main_conf, instantiated_stage_confs, data)

        return model, metrics, feat_importance, fit_err_msg

    @staticmethod
    # def instantiate_fit(template_conf_dir, data_conf_path, spark):
    def instantiate_fit(data_conf, template_main_conf, template_stage_confs, spark, data_host='file://'):
        """
        Based on the template_conf_dir and data_conf_path, instantiate and fit the pipeline model
        @:return model Pipeline model
        @:return metrics Pipeline Model evaluation metrics
        @:return feat_importance Model feature importance, can be None
        """

        instantiated_main_conf, instantiated_stage_confs, err_msg = \
            SparkMLPipe.instantiate(data_conf, template_main_conf, template_stage_confs)

        if err_msg is not None:
            return None, None, None, err_msg

        return SparkMLPipe.fit(instantiated_main_conf, instantiated_stage_confs, spark, data_host)
