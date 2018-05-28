from collections import OrderedDict

from goodreads_api_client.resources import Shelf
from goodreads_api_client.tests.resources.conftest import ResourceTestCase
from goodreads_api_client.tests.conftest import vcr


class TestShelf(ResourceTestCase):
    def setUp(self):
        self._shelf = Shelf(transport=self._transport)

    @vcr.use_cassette('shelf/list.yaml')
    def test_list(self):
        result = self._shelf.list('13686342')
        shelves = result['user_shelf']

        self.assertEqual(len(shelves), 25)
        self.assertEqual(shelves[0]['id'], OrderedDict([
            ('@type', 'integer'), ('#text', '44154681')]))
        self.assertEqual(shelves[0]['name'], 'read')
