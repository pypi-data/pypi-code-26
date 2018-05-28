from goodreads_api_client.resources import Series
from goodreads_api_client.tests.resources.conftest import ResourceTestCase
from goodreads_api_client.tests.conftest import vcr


class TestSeries(ResourceTestCase):
    def setUp(self):
        self._series = Series(transport=self._transport)

    @vcr.use_cassette('series/list.yaml')
    def test_list(self):
        result = self._series.list('38550')

        self.assertEqual(len(result), 119)
        self.assertEqual(result[0]['id'], '982770')
        self.assertEqual(result[0]['series']['title'],
                         'The Stormlight Archive (GraphicAudio)')

    @vcr.use_cassette('series/show.yaml')
    def test_show(self):
        result = self._series.show('40911')

        self.assertEqual(result['id'], '40911')
        self.assertEqual(result['title'], 'Saga o Wiedźminie')

    @vcr.use_cassette('series/work.yaml')
    def test_work(self):
        result = self._series.work('8134945')

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], '178728')
        self.assertEqual(result[0]['series']['title'],
                         'The Stormlight Archive')
