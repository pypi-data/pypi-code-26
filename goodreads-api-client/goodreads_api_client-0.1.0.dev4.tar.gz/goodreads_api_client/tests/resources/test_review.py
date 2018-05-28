from goodreads_api_client.resources import Review
from goodreads_api_client.tests.resources.conftest import ResourceTestCase
from goodreads_api_client.tests.conftest import vcr


class TestReview(ResourceTestCase):
    def setUp(self):
        self._review = Review(transport=self._transport)

    @vcr.use_cassette('review/recent_reviews.yaml')
    def test_recent_reviews(self):
        result = self._review.recent_reviews()

        self.assertTrue(len(result) > 0)

    @vcr.use_cassette('review/show.yaml')
    def test_show(self):
        result = self._review.show('21')

        self.assertEqual(result['id'], '21')
        self.assertEqual(str(result['rating']), '5')

    @vcr.use_cassette('review/show_by_user_and_book.yaml')
    def test_show_by_user_and_book(self):
        result = self._review.show_by_user_and_book(book_id='50', user_id='1')

        self.assertEqual(result['id'], '21')
        self.assertEqual(str(result['rating']), '5')
