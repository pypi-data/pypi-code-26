from .base import BaseStageHandler
from ...utils import util


class ImputerHandler(BaseStageHandler):
    # TODO
    def _validate(self):
        return True

    def _gen_input_assembler(self):
        return None

    def _gen_stage(self):
        stage_conf = dict()

        stage_conf['class'] = 'pyspark.ml.feature.Imputer'
        stage_conf['uid'] = util.random_uid('Imputer')
        stage_conf['paramMap'] = dict()
        stage_conf['paramMap']['strategy'] = self.conf['paramMap']['strategy']

        stage_conf['paramMap']['inputCols'] = self.inputs
        stage_conf['paramMap']['outputCols'] = ['_'.join([inputCol, stage_conf['uid'], 'output_col'])
                                                for inputCol in self.inputs]

        stage = util.StageConfigReader.load(stage_conf)

        return stage


class MinMaxScalerHandler(BaseStageHandler):
    # TODO
    def _validate(self):
        return True

    def _gen_input_assembler(self):

        if isinstance(self.inputs, str):
            return None

        stage_conf = dict()

        stage_conf['class'] = 'pyspark.ml.feature.VectorAssembler'
        stage_conf['uid'] = util.random_uid('VectorAssembler')
        stage_conf['paramMap'] = dict()

        stage_conf['paramMap']['inputCols'] = self.inputs
        stage_conf['paramMap']['outputCol'] = '_'.join([stage_conf['uid'], 'output_vec'])

        assembler = util.StageConfigReader.load(stage_conf)
        return assembler

    def _gen_stage(self):
        stage_conf = dict()

        stage_conf['class'] = 'pyspark.ml.feature.MinMaxScaler'
        stage_conf['uid'] = util.random_uid('MinMaxScaler')
        stage_conf['paramMap'] = dict()

        inputCol = self.assembler.getOutputCol() if self.assembler is not None else self.inputs
        stage_conf['paramMap']['inputCol'] = inputCol
        stage_conf['paramMap']['outputCol'] = '_'.join([inputCol, stage_conf['uid'], 'output_vec'])

        stage = util.StageConfigReader.load(stage_conf)

        return stage
