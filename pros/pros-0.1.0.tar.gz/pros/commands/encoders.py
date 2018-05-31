from urllib.parse import quote_plus
from pros import Command, catalog


@catalog.register
class URLEncoder(Command):
    """Encode text to URL safe string
    """
    name = 'encode/url'
    implement = frozenset({'text', 'string'})
    sources = frozenset({'text'})

    def process(self):
        while 1:
            source, message = yield
            yield quote_plus(message)
