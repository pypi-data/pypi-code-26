class VariableState:

    def __init__(self, strings):
        self.name = strings[0]
        self.line = strings[1]
        self.value = strings[2]
        self.function = strings[3]

    def __str__(self):
        return "var " + str(self.name) + " = " + str(self.value) + " | line: " + str(self.line) + " | function: " + str(self.function)


        