import os
from pyspark.ml import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from ..utils import util
from ..utils import constants


class BasePipeBuilder:
    # TODO
    # check types in data_conf are fine
    # make sure label col is not in features
    # check if label col is real type
    def _validate_data(self, data_conf):
        return True

    def instantiate(self, stage_conf_list, data_conf):
        raise NotImplementedError()

    def build(self, instantiated_main_conf, instantiated_stage_confs):
        raise NotImplementedError()

    def fit(self, data):
        raise NotImplementedError()

    def get_model(self):
        return self.model

    def get_metrics(self, data):
        raise NotImplementedError()

    def get_feat_importance(self):
        raise NotImplementedError()

    @staticmethod
    def load_handler(stage_conf):
        handler_type = util.get_class(stage_conf['class'])

        return handler_type(stage_conf)


class RandomForestRegressorPipeBuilder(BasePipeBuilder):
    def __init__(self):
        super().__init__()
        self.stage_classes = ['sparkmlpipe.mlpipe.handler.feature.ImputerHandler',
                              'sparkmlpipe.mlpipe.handler.feature.MinMaxScalerHandler',
                              'sparkmlpipe.mlpipe.handler.regression.RandomForestRegressorHandler']

        self.name = util.random_uid("随机森林回归")
        self.uid = util.random_uid("Pipeline")
        self.pipeline = None
        self.model = None
        self.label_col = None

    def _instantiate_main_conf(self, instantiated_stage_confs, data_conf):
        instantiated_main_conf = dict()
        instantiated_main_conf['name'] = self.name
        instantiated_main_conf['uid'] = self.uid
        instantiated_main_conf['version'] = constants.CONF_VERSION
        instantiated_main_conf['class'] = 'sparkmlpipe.mlpipe.mlpipe_builder.RandomForestRegressorPipeBuilder'

        instantiated_main_conf['stages'] = []

        for instantiated_stage_conf in instantiated_stage_confs:
            instantiated_main_conf['stages'].append(instantiated_stage_conf['uid'])

        instantiated_main_conf['data'] = data_conf
        return instantiated_main_conf

    def instantiate(self, stage_conf_list, data_conf):
        is_valid = self._validate_data(data_conf)

        if is_valid:
            header = data_conf['feat_header']
            types = data_conf['feat_types']

            num_cols = [header[i] for i, typ in enumerate(types) if typ in constants.REAL_TYPES]
            self.label_col = data_conf['label_col']

            instantiated_stage_confs = []
            inputs = num_cols

            # numeric stages
            for index, stage_conf in enumerate(stage_conf_list[:-1]):
                if stage_conf['class'] == self.stage_classes[index]:
                    pass
                else:
                    raise RuntimeError('Require class: {0}, but get class {1}'.format(self.stage_classes[index],
                                                                                      stage_conf['class']))

                stage_handler = BasePipeBuilder.load_handler(stage_conf)
                current_stage_confs = stage_handler.process(inputs, None)

                if 'outputCol' in current_stage_confs[-1]['paramMap']:
                    inputs = current_stage_confs[-1]['paramMap']['outputCol']
                elif 'outputCols' in current_stage_confs[-1]['paramMap']:
                    inputs = current_stage_confs[-1]['paramMap']['outputCols']

                instantiated_stage_confs.extend(current_stage_confs)

            # model stage
            stage_conf = stage_conf_list[-1]
            if stage_conf['class'] == self.stage_classes[-1]:
                pass
            else:
                raise RuntimeError('Require class: {0}, but get class {1}'.format(self.stage_classes[index],
                                                                                  stage_conf['class']))
            stage_handler = BasePipeBuilder.load_handler(stage_conf)
            model_stage_confs = stage_handler.process(inputs, self.label_col)
            instantiated_stage_confs.extend(model_stage_confs)

            instantiated_main_conf = self._instantiate_main_conf(instantiated_stage_confs, data_conf)

            return instantiated_main_conf, instantiated_stage_confs
        else:
            raise RuntimeError("Data conf error in RandomForestRegressorPipeBuilder")

    def build(self, instantiated_main_conf, instantiated_stage_confs):
        self.pipeline = util.PipelineLoader.load(instantiated_stage_confs, instantiated_main_conf)

    def fit(self, data):
        if self.pipeline is None:
            raise RuntimeError("Pipeline is not built. Call build() before fit()")
        self.model = self.pipeline.fit(data)
        self.model._resetUid(self.pipeline.uid)
        for index, stage in enumerate(self.model.stages):
            stage._resetUid(self.pipeline.getStages()[index].uid)

    def get_metrics(self, data):
        predictions = self.model.transform(data)

        predictions_df = predictions.select([self.label_col, 'prediction']).toPandas()
        y_true = predictions_df[self.label_col]
        y_pred = predictions_df['prediction']

        metrics = dict()

        metrics['r2_score'] = r2_score(y_true, y_pred)
        metrics['mean_squared_error'] = mean_squared_error(y_true, y_pred)
        metrics['mean_absolute_error'] = mean_absolute_error(y_true, y_pred)

        return metrics

    def get_feat_importance(self):
        return self.model.stages[-1].featureImportances
