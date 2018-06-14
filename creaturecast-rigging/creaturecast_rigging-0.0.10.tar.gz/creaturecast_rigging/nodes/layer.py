layers = []

class Layer(object):

    def __new__(cls, *args, **kwargs):
        new_class = object.__new__(cls, *args, **kwargs)
        return new_class

    def __init__(self, name):
        super(Layer, self).__init__()
        layers.append(self)
        self.name = name