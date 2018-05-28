from goodreads_api_client.resources import UserStatus
from goodreads_api_client.tests.resources.conftest import ResourceTestCase
from goodreads_api_client.tests.conftest import vcr


class TestUserStatus(ResourceTestCase):
    def setUp(self):
        self._status = UserStatus(transport=self._transport)

    @vcr.use_cassette('user_status/show.yaml')
    def test_show(self):
        result = self._status.show('13686342')

        self.assertEqual(result['id'], '13686342')
        self.assertEqual(result['page'], '18')
