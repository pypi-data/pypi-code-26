import re
from pros import Command, catalog


@catalog.register
class RegexpFilter(Command):
    """Output message if it is match to regular expression.
    """
    name = 'filter/regexp'
    implement = frozenset()
    sources = frozenset({'text'})

    @staticmethod
    def get_parser(parser):
        parser.add_argument('--expr', default=r'^\d$')
        return parser

    def process(self, expr):
        rex = re.compile(expr)
        while 1:
            source, message = yield
            if rex.match(message):
                yield message
