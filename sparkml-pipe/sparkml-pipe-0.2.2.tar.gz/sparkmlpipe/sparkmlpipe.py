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
        # main_conf_path = os.path.join(template_conf_dir, "main.yaml")
        # main_conf = util.load_config(main_conf_path)
        #
        # mlpipe_builder_type = util.get_class(main_conf['class'])
        # mlpipe_builder = mlpipe_builder_type()
        #
        # stage_conf_dir = os.path.join(template_conf_dir, "stages/")
        #
        # stage_conf_list = util.load_stage_conf_list(main_conf, stage_conf_dir)
        # data_conf = util.load_config(data_conf_path)

        mlpipe_builder_type = util.get_class(template_main_conf['class'])
        mlpipe_builder = mlpipe_builder_type()

        instantiated_main_conf, instantiated_stage_conf_list = mlpipe_builder.instantiate(data_conf,
                                                                                          template_stage_confs)
        return instantiated_main_conf, instantiated_stage_conf_list

    @staticmethod
    # def fit(instantiated_conf_dir, spark):
    def fit(instantiated_main_conf, instantiated_stage_confs, spark):
        """
        Based on the instantiated_conf_dir, instantiate and fit the pipeline model
        @:return model Pipeline model
        @:return metrics Pipeline Model evaluation metrics
        @:return feat_importance Model feature importance, can be None
        """
        # instantiated_main_conf_path = os.path.join(instantiated_conf_dir, "main.yaml")
        # instantiated_main_conf = util.load_config(instantiated_main_conf_path)
        #
        # mlpipe_builder_type = util.get_class(instantiated_main_conf['class'])
        # mlpipe_builder = mlpipe_builder_type()
        #
        # instantiated_stage_conf_dir = os.path.join(instantiated_conf_dir, "stages/")
        # instantiated_stage_conf_list = util.load_stage_conf_list(instantiated_main_conf, instantiated_stage_conf_dir)

        mlpipe_builder_type = util.get_class(instantiated_main_conf['class'])
        mlpipe_builder = mlpipe_builder_type()

        data = spark.read.option('header', 'true')\
            .option("inferSchema", "true") \
            .csv(os.path.join(constants.ROOT_PATH, instantiated_main_conf['data']['location']))

        mlpipe_builder.build(instantiated_main_conf, instantiated_stage_confs)
        mlpipe_builder.fit(data)
        model = mlpipe_builder.get_model()
        metrics = mlpipe_builder.get_metrics(data)
        feat_importance = mlpipe_builder.get_feat_importance()

        return model, metrics, feat_importance

    @staticmethod
    # def instantiate_fit(template_conf_dir, data_conf_path, spark):
    def instantiate_fit(data_conf, template_main_conf, template_stage_confs, spark):
        """
        Based on the template_conf_dir and data_conf_path, instantiate and fit the pipeline model
        @:return model Pipeline model
        @:return metrics Pipeline Model evaluation metrics
        @:return feat_importance Model feature importance, can be None
        """

        instantiated_main_conf, instantiated_stage_confs = \
            SparkMLPipe.instantiate(data_conf, template_main_conf, template_stage_confs)

        # data = spark.read.option('header', 'true')\
        #     .option("inferSchema", "true") \
        #     .csv(os.path.join(constants.ROOT_PATH, instantiated_main_conf['data']['location']))

        model, metrics, feat_importance = SparkMLPipe.fit(instantiated_main_conf, instantiated_stage_confs, spark)

        return model, metrics, feat_importance
