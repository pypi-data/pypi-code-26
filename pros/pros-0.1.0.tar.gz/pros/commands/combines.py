from collections import defaultdict
from pros import Command, catalog


@catalog.register
class ConcatCombine(Command):
    """Concatenate strings from two or more sources.
    """
    name = 'combine/concat'
    implement = frozenset({'text'})
    sources = frozenset({'text'})

    @staticmethod
    def get_parser(parser):
        parser.add_argument('--sources', type=int, help='count of sources')
        parser.add_argument('--separator', default=':')
        return parser

    def process(self, sources, separator):
        messages = defaultdict(list)
        while 1:
            source, message = yield
            messages[source].append(message)
            if sum(int(bool(values)) for values in messages) >= sources:
                yield separator.join(values.pop(0) for values in messages)
