from datasette import hookimpl
from vtfunc import TableFunction
import re
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen


class Scraper(TableFunction):
    params = ['url']
    columns = ['href', 'description']
    name = 'scraper'

    def initialize(self, url):
        try:
            self._iter = re.finditer(
                '<a[^\>]+?href="([^\"]+?)"[^\>]*?>([^\<]+?)</a>',
                urlopen(url).read().decode('utf-8'))
        except Exception as e:
            print(e)
            self._iter = []

    def iterate(self, idx):
        return next(self._iter).groups()


@hookimpl
def prepare_connection(conn):
    Scraper.register(conn)
