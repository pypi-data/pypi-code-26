from .base import BaseStageHandler
from ...utils import util


class ImputerHandler(BaseStageHandler):
    def __init__(self, conf):
        super(ImputerHandler, self).__init__(conf)
        self.class_path = "pyspark.ml.feature.Imputer"
        self.uid = util.random_uid(self.class_path.split('.')[-1])

    def _validate(self):
        # inputs must be list
        if isinstance(self.inputs, list) is False:
            return False,  self.uid + "'s inputs " + str(self.inputs) + " is not a list"

        # outputs must be None
        if self.outputs is not None:
            return False, self.uid + "'s outputs " + str(self.outputs) + " is not None"

        return True, None

    def _gen_input_assembler_conf(self):
        return None

    def _gen_stage_conf(self):
        stage_conf = dict()

        stage_conf['class'] = self.class_path
        stage_conf['uid'] = self.uid
        stage_conf['paramMap'] = dict()
        stage_conf['paramMap']['strategy'] = self.conf['paramMap']['strategy']

        stage_conf['paramMap']['inputCols'] = self.inputs
        stage_conf['paramMap']['outputCols'] = ['_'.join([inputCol, stage_conf['uid'], 'output_col'])
                                                for inputCol in self.inputs]

        return stage_conf


class MinMaxScalerHandler(BaseStageHandler):
    def __init__(self, conf):
        super(MinMaxScalerHandler, self).__init__(conf)
        self.class_path = "pyspark.ml.feature.MinMaxScaler"
        self.uid = util.random_uid(self.class_path.split('.')[-1])

    def _validate(self):
        # outputs must be None
        if self.outputs is not None:
            return False, self.uid + "'s outputs " + str(self.outputs) + " is not None"
        return True, None

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

        stage_conf['class'] = self.class_path
        stage_conf['uid'] = self.uid
        stage_conf['paramMap'] = dict()

        inputCol = self.assembler_conf['paramMap']['outputCol'] if self.assembler_conf is not None else self.inputs
        stage_conf['paramMap']['inputCol'] = inputCol
        stage_conf['paramMap']['outputCol'] = '_'.join([inputCol, stage_conf['uid'], 'output_vec'])

        return stage_conf
