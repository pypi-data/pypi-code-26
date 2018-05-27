class FunctionActivation:

    def __init__(self, strings):
        self.activation_id = strings[0]
        self.name = strings[1]
        self.line = strings[2]
        self.func_return = strings[3]
        self.caller_id = strings[4]

    def has_caller(self):
        if (self.caller_id is None):
            return False
        else:
            return True
        