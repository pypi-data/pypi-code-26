from goodreads_api_client.resources import Comment
from goodreads_api_client.tests.resources.conftest import ResourceTestCase
from goodreads_api_client.tests.conftest import vcr


class TestComment(ResourceTestCase):
    def setUp(self):
        self._comment = Comment(transport=self._transport)

    @vcr.use_cassette('comment/list.yaml')
    def test_list(self):
        result = self._comment.list(id_='792532185', resource_type='review')
        comments = result['comment']

        self.assertTrue(comments)
        self.assertEqual(comments[0]['id'], '166718067')
