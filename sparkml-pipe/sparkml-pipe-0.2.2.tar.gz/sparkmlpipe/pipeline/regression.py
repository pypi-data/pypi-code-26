# -*- encoding: utf-8 -*-
from pyspark.ml.regression import LinearRegression, RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from .base import BasePipelineBuilder
from ..utils.constants import LINEAR_REGRESSION_REGRESSOR, RANDOM_FOREST_REGRESSOR
from ..utils.exceptions import InvalidConfigItemError


class RegressionPipelineBuilder(BasePipelineBuilder):
    def get_metrics(self, y_true, y_pred):
        metrics = dict()

        metrics['r2_score'] = r2_score(y_true, y_pred)
        metrics['mean_squared_error'] = mean_squared_error(y_true, y_pred)
        metrics['mean_absolute_error'] = mean_absolute_error(y_true, y_pred)

        return metrics

    def _get_model_stages(self):
        model_stages = []
        model_conf = self.config['pipe']['model']
        params = model_conf['params'] if 'params' in model_conf else {}
        if model_conf['type'] == LINEAR_REGRESSION_REGRESSOR:
            model = LinearRegression(featuresCol=self.feat_col, labelCol=self.label_col)
            if 'maxIter' in params:
                model.setMaxIter(params['maxIter'])
            if 'regParam' in params:
                model.setRegParam(params['regParam'])
            if 'elasticNetParam' in params:
                model.setElasticNetParam(params['elasticNetParam'])

        elif model_conf['type'] == RANDOM_FOREST_REGRESSOR:
            model = RandomForestRegressor(featuresCol=self.feat_col, labelCol=self.label_col)
            if 'seed' in params:
                model.setSeed(params['seed'])
            if 'numTrees' in params:
                model.setNumTrees(params['numTrees'])
            if 'maxDepth' in params:
                model.setMaxDepth(params['maxDepth'])
            if 'subsamplingRate' in params:
                model.setSubsamplingRate(params['subsamplingRate'])
        else:
            raise InvalidConfigItemError('pipe.model.type', model_conf['type'])

        model_stages.append(model)
        return model_stages
