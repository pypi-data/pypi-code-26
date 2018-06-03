from .base import BaseStageHandler
from ...utils import util


class RandomForestRegressorHandler(BaseStageHandler):
    # TODO
    def _validate(self):
        return True

    def _gen_input_assembler_conf(self):
        if isinstance(self.inputs, str):
            return None

        stage_conf = dict()

        stage_conf['class'] = 'pyspark.ml.feature.VectorAssembler'
        stage_conf['uid'] = util.random_uid('VectorAssembler')
        stage_conf['paramMap'] = dict()

        stage_conf['paramMap']['inputCols'] = self.inputs
        stage_conf['paramMap']['outputCol'] = '_'.join([stage_conf['uid'], 'output_vec'])

        return stage_conf

    def _gen_stage_conf(self):
        stage_conf = dict()

        stage_conf['class'] = 'pyspark.ml.regression.RandomForestRegressor'
        stage_conf['uid'] = util.random_uid('RandomForestRegressor')
        stage_conf['paramMap'] = dict()

        stage_conf['paramMap']['seed'] = self.conf['paramMap']['seed']
        stage_conf['paramMap']['numTrees'] = self.conf['paramMap']['numTrees']
        stage_conf['paramMap']['maxDepth'] = self.conf['paramMap']['maxDepth']
        stage_conf['paramMap']['subsamplingRate'] = self.conf['paramMap']['subsamplingRate']

        inputCol = self.assembler_conf['paramMap']['outputCol'] if self.assembler_conf is not None else self.inputs
        stage_conf['paramMap']['featuresCol'] = inputCol
        stage_conf['paramMap']['labelCol'] = self.outputs

        return stage_conf
