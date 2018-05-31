import sys
from pros import Command, catalog


class BaseOutput(Command):
    sources = frozenset({'text'})

    def process(self, name=None):
        custom = self._file is None
        if custom:
            self._file = open(name, 'w')

        while 1:
            source, message = yield
            print(message, file=self._file)

        if custom:
            self._file.close()


@catalog.register
class StdoutOutput(BaseOutput):
    name = 'output/stdout'
    _file = sys.stdout


@catalog.register
class StderrOutput(BaseOutput):
    name = 'output/stderr'
    _file = sys.stderr


@catalog.register
class FileOutput(BaseOutput):
    name = 'output/file'
    _file = None

    @staticmethod
    def get_parser(parser):
        parser.add_argument('--name', default='out.txt')
        return parser
