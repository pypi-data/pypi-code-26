from pros import Command, catalog


@catalog.register
class StrTransform(Command):
    """Transform any message to string.
    """
    name = 'transform/string'
    implement = frozenset({'text', 'string'})
    sources = frozenset({'integer'})

    def process(self):
        while 1:
            source, message = yield
            if isinstance(source, bytes):
                yield source.encode('utf-8')
            else:
                yield str(message)


@catalog.register
class MultiplyTransform(Command):
    """Multiply integer numbers to n.
    """
    name = 'transform/multiply'
    implement = frozenset({'integer', 'number'})
    sources = frozenset({'integer', 'number'})

    @staticmethod
    def get_parser(parser):
        parser.add_argument('-n', '--multiplier', type=int, default=2)
        return parser

    def process(self, multiplier):
        while 1:
            source, message = yield
            yield message * multiplier
