from string import ascii_letters
from itertools import product
from pros import Command, catalog


@catalog.register
class IntegersGenerator(Command):
    """Return sequence of integers from start (inclusive) to stop (inclusive) by step.
    """
    name = 'generate/integers'
    implement = frozenset({'integer', 'number'})
    sources = frozenset({'root'})

    @staticmethod
    def get_parser(parser):
        parser.add_argument('--start', type=int, default=1)
        parser.add_argument('--stop', type=int)
        parser.add_argument('--step', type=int, default=1, help='can be negative')
        return parser

    def process(self, start, stop, step):
        yield
        yield from range(start, stop + 1, step)


@catalog.register
class WordsGenerator(Command):
    """Return sequence of symbols from start (inclusive) to stop (inclusive) length.
    """
    name = 'generate/words'
    implement = frozenset({'word', 'text'})
    sources = frozenset({'root'})

    @staticmethod
    def get_parser(parser):
        parser.add_argument('--alphabet', default=ascii_letters)
        parser.add_argument('--start', type=int, default=4, help='minimum length')
        parser.add_argument('--stop', type=int, default=4, help='maximum length')
        return parser

    def process(self, alphabet, start, stop):
        yield
        for length in range(start, stop):
            for letters in product(*([alphabet] * length)):
                yield ''.join(letters)
