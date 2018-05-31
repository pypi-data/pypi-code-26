import sys
from pros import Command, catalog


class BaseInput(Command):
    sources = frozenset({'text'})

    def process(self, name=None, lines=None):
        yield
        custom = self._file is None
        if custom:
            self._file = open(name, 'r')
        for k, message in enumerate(self._file):
            yield message
            if lines and k >= lines:
                break
        if custom:
            self._file.close()


@catalog.register
class StdinInput(BaseInput):
    name = 'input/stdin'
    _file = sys.stdin

    @staticmethod
    def get_parser(parser):
        parser.add_argument('--lines', type=int, help="Maximum readed lines")
        return parser


@catalog.register
class FileInput(BaseInput):
    name = 'input/file'
    _file = None

    @staticmethod
    def get_parser(parser):
        parser.add_argument('--name', default='in.txt')
        parser.add_argument('--lines', type=int, help="Maximum readed lines")
        return parser
