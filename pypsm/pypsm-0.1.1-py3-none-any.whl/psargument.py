
class PSArgument(object):
    """An Argument to a PSFunction"""
    def __init__(self, name, pstype, default=None):
        self.name = name
        self.type = pstype
        self.default = default
        self.required = default is None

    def __str__(self):
        return ('PSArgument(name=%s, type=%s, required=%s'
                % (self.name, self.type, self.required))

    def __repr__(self):
        return self.__str__()


    def __call__(self, value):
        if self.required and not value:
            raise TypeError('Argument %s is required' % self.name)

        if value:
            return self.type(value)

        if callable(self.default): # Allow default to be callable
            return self.default()

        return self.default
