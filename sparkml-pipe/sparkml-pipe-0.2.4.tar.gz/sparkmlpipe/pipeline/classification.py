# -*- encoding: utf-8 -*-
from pyspark.ml.classification import LogisticRegression, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from .base import BasePipelineBuilder
from ..utils.constants import LOGISTIC_REGRESSION_CLASSIFIER, RANDOM_FOREST_CLASSIFIER
from ..utils.exceptions import InvalidConfigItemError


class ClassificationPipelineBuilder(BasePipelineBuilder):

    def get_metrics(self, y_true, y_pred):
        metrics = dict()

        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        metrics['weighted_f1'] = f1_score(y_true, y_pred, average='weighted')
        metrics['weighted_precision'] = precision_score(y_true, y_pred, average='weighted')
        metrics['weighted_recall'] = recall_score(y_true, y_pred, average='weighted')

        return metrics

    def _get_model_stages(self):
        model_stages = []
        model_conf = self.config['pipe']['model']
        params = model_conf['params'] if 'params' in model_conf else {}
        if model_conf['type'] == LOGISTIC_REGRESSION_CLASSIFIER:
            model = LogisticRegression(featuresCol=self.feat_col, labelCol=self.label_col)
            if 'maxIter' in params:
                model.setMaxIter(params['maxIter'])
            if 'regParam' in params:
                model.setRegParam(params['regParam'])
            if 'elasticNetParam' in params:
                model.setElasticNetParam(params['elasticNetParam'])
        elif model_conf['type'] == RANDOM_FOREST_CLASSIFIER:
            model = RandomForestClassifier(featuresCol=self.feat_col, labelCol=self.label_col)
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
