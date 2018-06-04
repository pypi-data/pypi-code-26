import pickle


class sendableData():
    """ Sendable data type. """

    def __init__(self, data):
        bytes.__init__(self)

        if type(data) == bytes:
            self.data = data
        else:
            self.data = pickle.dumps(data)

        self.decodedData = pickle.loads(self.data)

    def get(self):
        return self.data

    def decoded(self):
        return self.decodedData
