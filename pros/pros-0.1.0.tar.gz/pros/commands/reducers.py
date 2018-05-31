from pros import Command, catalog


@catalog.register
class SumReducer(Command):
    """Sum all numbers
    """
    name = 'reduce/sum'
    implement = frozenset({'integer', 'float', 'number'})
    sources = frozenset({'number'})

    def process(self):
        self.x = 0
        while 1:
            source, message = yield
            self.x += message

    def finish(self):
        return [self.x]
