from goodreads_api_client.resources import User
from goodreads_api_client.tests.resources.conftest import ResourceTestCase
from goodreads_api_client.tests.conftest import vcr


class TestUser(ResourceTestCase):
    def setUp(self):
        self._user = User(transport=self._transport)

    @vcr.use_cassette('user/show.yaml')
    def test_show(self):
        result = self._user.show('13686342')

        self.assertEqual(result['id'], '13686342')
        self.assertEqual(result['name'], 'Michelle Zhang')
