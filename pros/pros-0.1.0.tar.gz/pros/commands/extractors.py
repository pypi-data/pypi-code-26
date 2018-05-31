import re
from pros import Command, catalog


@catalog.register
class RegexpExtractor(Command):
    """Extract substring from message by regular expression.
    """
    name = 'extract/regexp'
    implement = frozenset()
    sources = frozenset({'text'})

    @staticmethod
    def get_parser(parser):
        parser.add_argument('--expr', default=r'\w')
        return parser

    def process(self, expr):
        rex = re.compile(expr)
        while 1:
            source, message = yield
            for substring in rex.findall(message):
                yield substring
