from goodreads_api_client.resources import Recommendation
from goodreads_api_client.tests.resources.conftest import ResourceTestCase
from goodreads_api_client.tests.conftest import vcr


class TestRecommendation(ResourceTestCase):
    def setUp(self):
        self._recommendation = Recommendation(transport=self._transport)

    @vcr.use_cassette('recommendation/show.yaml')
    def test_show(self):
        result = self._recommendation.show('25047806')

        self.assertEqual(result['id'], '25047806')
        self.assertEqual(str(result['likes_count']), '0')
