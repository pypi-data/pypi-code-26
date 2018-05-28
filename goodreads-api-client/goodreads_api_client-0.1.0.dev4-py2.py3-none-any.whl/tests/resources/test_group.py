from goodreads_api_client.resources import Group
from goodreads_api_client.tests.resources.conftest import ResourceTestCase
from goodreads_api_client.tests.conftest import vcr


class TestGroup(ResourceTestCase):
    def setUp(self):
        self._group = Group(transport=self._transport)

    @vcr.use_cassette('group/list.yaml')
    def test_list(self):
        result = self._group.list(user_id='13686342')

        self.assertEqual(int(result['count']), 0)

    @vcr.use_cassette('group/members.yaml')
    def test_members(self):
        result = self._group.members('1')
        members = result['group_user']

        self.assertEqual(len(members), 30)

    @vcr.use_cassette('group/search.yaml')
    def test_search(self):
        result = self._group.search(q='adventure')

        self.assertTrue(len(result) > 0)

    @vcr.use_cassette('group/show.yaml')
    def test_show(self):
        result = self._group.show('1')

        self.assertEqual(result['id'], '1')
        self.assertEqual(result['title'], 'Goodreads Feedback')
