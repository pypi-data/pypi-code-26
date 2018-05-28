from goodreads_api_client.resources import Book
from goodreads_api_client.tests.resources.conftest import ResourceTestCase
from goodreads_api_client.tests.conftest import vcr


class TestBook(ResourceTestCase):
    def setUp(self):
        self._book = Book(transport=self._transport)

    @vcr.use_cassette('book/id_to_work_id.yaml')
    def test_id_to_work_id(self):
        result = self._book.id_to_work_id(['1842', '1867'])

        self.assertEqual(result['item'], ['2138852', '5985'])

    @vcr.use_cassette('book/review_counts.yaml')
    def test_review_counts(self):
        result = self._book.review_counts(['0441172717'])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 53732)
        self.assertEqual(result[0]['isbn'], '0441172717')
        self.assertEqual(result[0]['isbn13'], '9780441172719')

    @vcr.use_cassette('book/show.yaml')
    def test_show(self):
        book_dict = self._book.show('50')

        self.assertEqual(book_dict['id'], '50')
        self.assertEqual(book_dict['title'], "Hatchet (Brian's Saga, #1)")

    @vcr.use_cassette('book/show_by_isbn.yaml')
    def test_show_by_isbn(self):
        result = self._book.show_by_isbn('0441172717')

        self.assertEqual(result['id'], '53732')
        self.assertEqual(result['title'], 'Dune')

    @vcr.use_cassette('book/title.yaml')
    def test_title(self):
        result = self._book.title(author='Arthur Conan Doyle',
                                  title='Hound of the Baskervilles')

        self.assertEqual(result['id'], '8921')
        self.assertEqual(result['title'], 'The Hound of the Baskervilles')
