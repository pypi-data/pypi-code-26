from abc import ABCMeta


class BaseStageHandler:
    __metaclass__ = ABCMeta

    def __init__(self, conf):
        self.conf = conf
        self.assembler = None
        self.inputs = None
        self.outputs = None

    def process(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs

        is_valid = self._validate()

        if not is_valid:
            raise RuntimeError(self.__class__.__name__ + " error during processing")

        stages = []
        self.assembler = self._gen_input_assembler()

        if self.assembler is None:
            self.inputs = inputs
        else:
            stages.append(self.assembler)
            self.inputs = self.assembler.getOutputCol()

        stages.append(self._gen_stage())

        return stages

    def _validate(self):
        raise NotImplementedError()

    def _gen_input_assembler(self):
        raise NotImplementedError()

    def _gen_stage(self):
        raise NotImplementedError()
