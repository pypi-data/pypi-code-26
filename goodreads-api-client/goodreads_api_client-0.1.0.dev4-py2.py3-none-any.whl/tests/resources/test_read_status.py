from goodreads_api_client.resources import ReadStatus
from goodreads_api_client.tests.resources.conftest import ResourceTestCase
from goodreads_api_client.tests.conftest import vcr


class TestReadStatus(ResourceTestCase):
    def setUp(self):
        self._read_status = ReadStatus(transport=self._transport)

    @vcr.use_cassette('read_status/show.yaml')
    def test_show(self):
        result = self._read_status.show('1')

        self.assertEqual(result['id'], '1')
        self.assertEqual(result['status'], 'read')
