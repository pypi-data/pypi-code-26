from goodreads_api_client.resources import Topic
from goodreads_api_client.tests.resources.conftest import ResourceTestCase
from goodreads_api_client.tests.conftest import vcr


class TestTopic(ResourceTestCase):
    def setUp(self):
        self._topic = Topic(transport=self._transport)

    @vcr.use_cassette('topic/group_folder.yaml')
    def test_group_folder(self):
        result = self._topic.group_folder('85538')

        self.assertEqual(result['id'], '85538')
        self.assertEqual(result['name'], 'Characters')

    @vcr.use_cassette('topic/show.yaml')
    def test_show(self):
        result = self._topic.show('693')

        self.assertEqual(result['id'], '693')
        self.assertEqual(result['author_user_id'], '122052')
