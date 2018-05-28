from collections import OrderedDict

from goodreads_api_client.resources import Author
from goodreads_api_client.tests.resources.conftest import ResourceTestCase
from goodreads_api_client.tests.conftest import vcr


class TestAuthor(ResourceTestCase):
    def setUp(self):
        self._author = Author(transport=self._transport)

    @vcr.use_cassette('author/books.yaml')
    def test_books(self):
        result = self._author.books('18541')
        books = result['book']

        self.assertEqual(len(result), 4)
        self.assertEqual(books[0]['id'], OrderedDict([('@type', 'integer'),
                                                      ('#text', '104744')]))
        self.assertEqual(books[0]['isbn'], '1565927249')

    @vcr.use_cassette('author/show.yaml')
    def test_show(self):
        result = self._author.show('18541')

        self.assertEqual(result['id'], '18541')
        self.assertEqual(result['name'], "Tim O'Reilly")
