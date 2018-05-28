from goodreads_api_client.resources import Event
from goodreads_api_client.tests.resources.conftest import ResourceTestCase
from goodreads_api_client.tests.conftest import vcr


class TestEvent(ResourceTestCase):
    def setUp(self):
        self._event = Event(transport=self._transport)

    @vcr.use_cassette('event/list.yaml')
    def test_list(self):
        result = self._event.list(
            country_code='US',
            lat='40.6771798',
            lng='-73.9766107',
            postal_code='11217',
        )
        events = result['event']

        self.assertTrue(len(events) > 0)
