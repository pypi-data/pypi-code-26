from urllib.parse import unquote_plus
from pros import Command, catalog


@catalog.register
class URLDecoder(Command):
    """Decode URL safe string to utf-8 text
    """
    name = 'decode/url'
    implement = frozenset({'text', 'string'})
    sources = frozenset({'text'})

    def process(self):
        while 1:
            source, message = yield
            yield unquote_plus(message)
