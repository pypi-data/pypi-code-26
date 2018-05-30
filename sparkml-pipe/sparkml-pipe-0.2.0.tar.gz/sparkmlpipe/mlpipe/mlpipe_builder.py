import os
from pyspark.ml import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from ..utils import util
from ..utils import constants


class BasePipeBuilder:
    def build(self, stage_confs_dir, data_conf):
        raise NotImplementedError()

    # TODO
    # check types in data_conf are fine
    # make sure label col is not in features
    # check if label col is real type
    def _validate_data(self, data_conf):
        return True

    def build(self):
        raise NotImplementedError()

    def fit(self):
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
        self.stage_ids = ['Imputer', 'MinMaxScaler', 'RandomForestRegressor']
        self.pipeline = None
        self.model = None
        self.label_col = None

    def build(self, stage_confs_dir, data_conf):
        is_valid = self._validate_data(data_conf)

        if is_valid:
            header = data_conf['feat_header']
            types = data_conf['feat_types']

            num_cols = [header[i] for i, typ in enumerate(types) if typ in constants.REAL_TYPES]
            self.label_col = data_conf['label_col']

            stages = []
            inputs = num_cols

            # numeric stages
            for index, stage_id in enumerate(self.stage_ids[:-1]):
                stage_sid = util.get_stage_sid(stage_id, index, len(self.stage_ids))
                stage_path = util.get_stage_path(stage_sid, stage_confs_dir)
                if os.path.isfile(stage_path):
                    stage_conf = util.load_config(stage_path)
                else:
                    RuntimeError('File don\'t exist: {0}'.format(stage_path))

                stage_handler = BasePipeBuilder.load_handler(stage_conf)
                current_stages = stage_handler.process(inputs, None)

                if current_stages[-1].hasParam('outputCol'):
                    inputs = current_stages[-1].getOutputCol()
                elif current_stages[-1].hasParam('outputCols'):
                    inputs = current_stages[-1].getOutputCols()

                stages.extend(current_stages)

            # model stage
            stage_sid = util.get_stage_sid(self.stage_ids[-1], len(self.stage_ids) - 1, len(self.stage_ids))
            stage_path = util.get_stage_path(stage_sid, stage_confs_dir)
            if os.path.isfile(stage_path):
                stage_conf = util.load_config(stage_path)
            else:
                RuntimeError('File don\'t exist: {0}'.format(stage_path))
            stage_handler = BasePipeBuilder.load_handler(stage_conf)
            model_stages = stage_handler.process(inputs, self.label_col)
            stages.extend(model_stages)

            self.pipeline = Pipeline(stages=stages)
        else:
            raise RuntimeError("Stage conf or data conf error in RandomForestRegressorPipeBuilder")

    def fit(self, data):
        self.model = self.pipeline.fit(data)

    def get_metrics(self, data):
        predictions = self.model.transform(data)

        predictions_df = predictions.select(self.label_col, 'prediction').toPandas()
        y_true = predictions_df[self.label_col]
        y_pred = predictions_df['prediction']

        metrics = dict()

        metrics['r2_score'] = r2_score(y_true, y_pred)
        metrics['mean_squared_error'] = mean_squared_error(y_true, y_pred)
        metrics['mean_absolute_error'] = mean_absolute_error(y_true, y_pred)

        return metrics

    def get_feat_importance(self):
        return self.model.stages[-1].featureImportances
