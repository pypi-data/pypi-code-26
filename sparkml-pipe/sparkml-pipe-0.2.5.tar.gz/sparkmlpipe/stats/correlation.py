# -*- encoding: utf-8 -*-
from pyspark.ml.stat import Correlation

from .base import BaseStatsBuilder
from sparkmlpipe.utils.exceptions import InvalidConfigItemError
from sparkmlpipe.utils.constants import PEARSON_CORR, SPEARMAN_CORR


class CorrelationBuilder(BaseStatsBuilder):

    def _get_stat(self, data):
        model_conf = self.config['pipe']['model']
        params = model_conf['params'] if 'params' in model_conf else {}

        if model_conf['type'] == PEARSON_CORR:
            corr = Correlation.corr(data, self.feat_col, 'pearson').collect()[0][0]
        elif model_conf['type'] == SPEARMAN_CORR:
            corr = Correlation.corr(data, self.feat_col, 'spearman').collect()[0][0]
        else:
            raise InvalidConfigItemError('pipe.model.type', model_conf['type'])
        return corr
