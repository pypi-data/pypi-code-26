from abc import ABCMeta


class BaseStageHandler:
    __metaclass__ = ABCMeta

    def __init__(self, conf):
        self.conf = conf
        self.assembler_conf = None
        self.inputs = None
        self.outputs = None

    def process(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs

        is_valid, err = self._validate()

        if not is_valid:
            raise RuntimeError(err)

        stage_confs = []
        self.assembler_conf = self._gen_input_assembler_conf()

        if self.assembler_conf is None:
            self.inputs = inputs
        else:
            stage_confs.append(self.assembler_conf)
            self.inputs = self.assembler_conf['paramMap']['outputCol']

        stage_confs.append(self._gen_stage_conf())

        return stage_confs

    # check the inputs and the outputs if they are suitable for the current stage
    def _validate(self):
        raise NotImplementedError()

    def _gen_input_assembler_conf(self):
        raise NotImplementedError()

    def _gen_stage_conf(self):
        raise NotImplementedError()
