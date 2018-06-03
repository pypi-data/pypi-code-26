# -*- encoding: utf-8 -*-
from abc import ABCMeta

from pyspark.ml import Pipeline
from pyspark.ml.feature import MinMaxScaler, StandardScaler, MaxAbsScaler, Imputer, VectorAssembler

from pyspark.ml.feature import StringIndexer, OneHotEncoderEstimator

from ..utils.exceptions import InvalidConfigItemError
from ..utils.constants import STRING_TYPE, REAL_TYPES, \
    MIN_MAX_SCALER_TYPE, STANDARD_SCALER_TYPE, MAXABS_SCALER_TYPE, \
    MEAN_IMPUTER_TYPE, MEDIAN_IMPUTER_TYPE


class BaseStatsBuilder:
    __metaclass__ = ABCMeta

    def __init__(self, config, data):
        self.config = config
        self.data = data
        self.num_out_cols = []
        self.str_out_cols = []
        self.feat_col = None

    def compute_stat(self):
        data_prep_stages = self._get_data_prep_stages()
        feat_prep_stages = self._get_feat_prep_stages()
        pipeline = Pipeline(stages=data_prep_stages + feat_prep_stages)

        prep_pipe = pipeline.fit(self.data)
        transformed_data = prep_pipe.transform(self.data)

        return self._get_stat(transformed_data)

    def _get_data_prep_stages(self):
        header = self.config['data']['header']
        types = self.config['data']['types']

        # preprocess numeric cols
        num_stages = []
        num_cols = [header[i] for i, typ in enumerate(types) if typ in REAL_TYPES]
        self.num_out_cols = num_cols

        imputer_conf = self.config['pipe']['data_prep']['numeric']['imputer']
        if len(num_cols) != 0 and imputer_conf != 0:
            imputer_cols = ['imputed_' + col for col in num_cols]
            if imputer_conf == MEAN_IMPUTER_TYPE:
                num_imputer = Imputer(inputCols=num_cols,
                                      outputCols=imputer_cols).setStrategy('mean')
            elif imputer_conf == MEDIAN_IMPUTER_TYPE:
                num_imputer = Imputer(inputCols=num_cols,
                                      outputCols=imputer_cols).setStrategy('median')
            else:
                raise InvalidConfigItemError('pipe.data_prep.numeric.imputer', imputer_conf)
            num_stages.append(num_imputer)
            self.num_out_cols = imputer_cols

        scaler_conf = self.config['pipe']['data_prep']['numeric']['scaler']
        if len(num_cols) != 0 and scaler_conf != 0:
            assembled_num_col_name = 'assembled_num_features'
            scaled_features_col_name = 'scaled_features'
            scaler_assembler = VectorAssembler(inputCols=self.num_out_cols, outputCol=assembled_num_col_name)
            if scaler_conf == MIN_MAX_SCALER_TYPE:
                num_scaler = MinMaxScaler(inputCol=assembled_num_col_name, outputCol=scaled_features_col_name)
            elif scaler_conf == STANDARD_SCALER_TYPE:
                num_scaler = StandardScaler(inputCol=assembled_num_col_name, outputCol=scaled_features_col_name)
            elif scaler_conf == MAXABS_SCALER_TYPE:
                num_scaler = MaxAbsScaler(inputCol=assembled_num_col_name, outputCol=scaled_features_col_name)
            else:
                raise InvalidConfigItemError('pipe.data_prep.numeric.scaler', scaler_conf)

            num_stages.append(scaler_assembler)
            num_stages.append(num_scaler)
            # overwrite the num out cols
            self.num_out_cols = [scaled_features_col_name]

        # preprocess string cols
        str_stages = []
        str_cols = [header[i] for i, typ in enumerate(types) if typ == STRING_TYPE]
        str_indexed_cols = [str_col + '_indexed' for str_col in str_cols]
        onehot_conf = self.config['pipe']['data_prep']['string']['onehot']
        if len(str_cols) != 0:
            if onehot_conf == 0:
                # str_indexer
                str_indexers = [
                    StringIndexer(inputCol=str_col,
                                  outputCol=str_out_col)
                    for str_col, str_out_col in zip(str_cols, str_indexed_cols)
                ]

                str_stages.extend(str_indexers)
                self.str_out_cols = str_indexed_cols

            elif onehot_conf == 1:
                # str_indexer
                str_indexers = [
                    StringIndexer(inputCol=str_col,
                                  outputCol=str_out_col)
                    for str_col, str_out_col in zip(str_cols, str_indexed_cols)
                ]

                # onehot_encoder
                str_vec_cols = [str_indexed_col + '_vec' for str_indexed_col in str_indexed_cols]
                str_encoder = OneHotEncoderEstimator(inputCols=str_indexed_cols,
                                                 outputCols=str_vec_cols)

                str_stages.extend(str_indexers)
                str_stages.append(str_encoder)
                self.str_out_cols = str_vec_cols
            else:
                raise InvalidConfigItemError('pipe.data_prep.string.onehot', onehot_conf)

        return num_stages + str_stages

    def _get_feat_prep_stages(self):
        feat_stages = []

        feat_name = self.config['pipe']['feat_prep']['name']

        input_cols = self.num_out_cols + self.str_out_cols

        if input_cols is []:
            raise RuntimeError('the input columns cannot be empty')

        feat_assembler = VectorAssembler(inputCols=input_cols, outputCol=feat_name)

        feat_stages.append(feat_assembler)

        self.feat_col = feat_name

        return feat_stages

    def _get_stat(self, data):
        raise NotImplementedError()
