class Variable:

    def __init__(self, model):
        self.model = model
        self._value = self.default

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class InputVariable(Variable):

    def __init__(self, model):
        super().__init__(model)


class OutputVariable(Variable):
    def __init__(self, model):
        super().__init__(model)

class Constant(Variable):
    def __init__(self, model):
        super().__init__(model)
