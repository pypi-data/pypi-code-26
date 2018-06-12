from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from ..utils import util
from ..utils import constants


class BasePipeBuilder:
    def _validate_data(self, data_conf):
        raise NotImplementedError()

    def instantiate(self, data_conf, stage_conf_list):
        raise NotImplementedError()

    def build(self, instantiated_main_conf, instantiated_stage_confs):
        raise NotImplementedError()

    def fit(self, data):
        raise NotImplementedError()

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

        self.pipeline = None
        self.model = None
        self.label_col = None

    def _validate_data(self, data_conf):
        # check feat_types in data_conf are in ALL_TYPES
        for index, typ in enumerate(data_conf['feat_types']):
            if typ not in constants.ALL_TYPES:
                return False, data_conf['feat_header'][index] + " has type " + typ + \
                       " not in " + str(constants.ALL_TYPES)
        # check all settings are there
        for item in ['name', 'version', 'location', 'feat_header', 'feat_types', 'label_col', 'label_type']:
            if item not in data_conf:
                return False, item + " is not in the data conf"

        # make sure label col is not in features
        if data_conf['label_col'] in data_conf['feat_header']:
            return False, "label col " + data_conf['label_col'] + " cannot be part of the feature columns"

        # make sure label col is real type
        if data_conf['label_type'] not in constants.REAL_TYPES:
            return False, data_conf['label_col'] + " has label type " + data_conf['label_type'] + \
                   " not in " + str(constants.REAL_TYPES)

        return True, None

    def _instantiate_main_conf(self, data_conf, instantiated_stage_confs):
        instantiated_main_conf = dict()
        instantiated_main_conf['name'] = util.random_uid("随机森林回归")
        instantiated_main_conf['uid'] = util.random_uid("Pipeline")
        instantiated_main_conf['version'] = constants.CONF_VERSION
        instantiated_main_conf['class'] = 'sparkmlpipe.mlpipe.mlpipe_builder.RandomForestRegressorPipeBuilder'

        instantiated_main_conf['stages'] = []

        for instantiated_stage_conf in instantiated_stage_confs:
            instantiated_main_conf['stages'].append(instantiated_stage_conf['uid'])

        instantiated_main_conf['data'] = data_conf
        return instantiated_main_conf

    def instantiate(self, data_conf, stage_confs):

        stage_classes = ['sparkmlpipe.mlpipe.handler.feature.ImputerHandler',
                         'sparkmlpipe.mlpipe.handler.feature.MinMaxScalerHandler',
                         'sparkmlpipe.mlpipe.handler.regression.RandomForestRegressorHandler']

        is_valid, err_msg = self._validate_data(data_conf)
        if not is_valid:
            return None, None, err_msg

        header = data_conf['feat_header']
        types = data_conf['feat_types']

        num_cols = [header[i] for i, typ in enumerate(types) if typ in constants.REAL_TYPES]

        instantiated_stage_confs = []
        inputs = num_cols

        # numeric stages
        for index, stage_conf in enumerate(stage_confs[:-1]):
            if stage_conf['class'] == stage_classes[index]:
                pass
            else:
                err_msg = 'Require class: {0}, but get class {1}'.format(stage_classes[index], stage_conf['class'])
                return None, None, err_msg

            stage_handler = BasePipeBuilder.load_handler(stage_conf)
            current_stage_confs, stage_err_msg = stage_handler.process(inputs, None)
            if stage_err_msg is not None:
                return None, None, stage_err_msg

            if 'outputCol' in current_stage_confs[-1]['paramMap']:
                inputs = current_stage_confs[-1]['paramMap']['outputCol']
            elif 'outputCols' in current_stage_confs[-1]['paramMap']:
                inputs = current_stage_confs[-1]['paramMap']['outputCols']

            instantiated_stage_confs.extend(current_stage_confs)

        # model stage
        stage_conf = stage_confs[-1]
        if stage_conf['class'] == stage_classes[-1]:
            pass
        else:
            err_msg = 'Require class: {0}, but get class {1}'.format(stage_classes[index], stage_conf['class'])
            return None, None, err_msg

        stage_handler = BasePipeBuilder.load_handler(stage_conf)
        model_stage_confs, stage_err_msg = stage_handler.process(inputs, data_conf['label_col'])
        if stage_err_msg is not None:
            return None, None, stage_err_msg

        instantiated_stage_confs.extend(model_stage_confs)

        instantiated_main_conf = self._instantiate_main_conf(data_conf, instantiated_stage_confs)

        return instantiated_main_conf, instantiated_stage_confs, None

    def fit(self, instantiated_main_conf, instantiated_stage_confs, train_data):

        # build the pipeline
        is_valid, err_msg = self._validate_data(instantiated_main_conf['data'])
        if not is_valid:
            return None, None, None, err_msg

        self.pipeline = util.PipelineLoader.load(instantiated_main_conf, instantiated_stage_confs)
        self.label_col = instantiated_main_conf['data']['label_col']

        # fit with the dataset
        fit_err_msg = self._fit(train_data)

        if fit_err_msg is not None:
            return None, None, None, fit_err_msg

        # get outputs
        metrics = self._get_metrics(train_data)
        feat_importance = self._get_feat_importance()

        return self.model, metrics, feat_importance, None

    def _fit(self, data):
        try:
            self.model = self.pipeline.fit(data)
        except BaseException as e:
            err_msg = 'Failed to excute spark pipeline: ' + str(e)
            return err_msg

        pipe_stages = self.pipeline.getStages()

        self.model._resetUid(self.pipeline.uid)
        for index, stage in enumerate(self.model.stages):
            # NOTE THAT the model estimator _resetUid doesn't work correctly, it still uses the old uid
            stage._resetUid(pipe_stages[index].uid)

        return None

    def _get_metrics(self, data):
        predictions = self.model.transform(data)

        predictions_df = predictions.select([self.label_col, 'prediction']).toPandas()
        y_true = predictions_df[self.label_col]
        y_pred = predictions_df['prediction']

        metrics = dict()

        metrics['r2_score'] = r2_score(y_true, y_pred)
        metrics['mean_squared_error'] = mean_squared_error(y_true, y_pred)
        metrics['mean_absolute_error'] = mean_absolute_error(y_true, y_pred)

        return metrics

    def _get_feat_importance(self):
        return self.model.stages[-1].featureImportances
