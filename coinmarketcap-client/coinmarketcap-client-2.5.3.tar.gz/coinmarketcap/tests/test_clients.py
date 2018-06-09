import vcr
from requests.exceptions import HTTPError

from unittest import TestCase
from unittest.mock import Mock, patch

from coinmarketcap.clients import (
    BaseClient, CryptoCoinTickerClient, CoinMarketCapClient, GlobalSummaryClient,
    ListCryptoCoinClient, TickerClient,
)
from coinmarketcap.constants import SupportedFormats
from coinmarketcap.parsers import DefaultParser, RequestKwargsParser


class BaseClientTestCase(TestCase):

    def setUp(self):
        self.stub_client_class = type(
            'StubClass',
            (BaseClient, ),
            {'PATH_URL': 'path'}
        )
        self.client = self.stub_client_class()

    def test_initializes_instance_correctly(self):
        self.assertEqual(
            'https://api.coinmarketcap.com/v2/', self.client.BASE_URL
        )

    def test_property_url_returns_correct_data(self):
        self.assertEqual(
            'https://api.coinmarketcap.com/v2/path', self.client.url
        )

    @patch('coinmarketcap.clients.requests')
    def test_get_calls_request_correctly(self, m_request):
        self.client.parser = Mock()
        self.client.parser.parse.return_value = {'1': 1}

        data = self.client.get()

        m_request.get.assert_called_once_with(self.client.url, params={})
        self.client.parser.parse.assert_called_once_with(
            m_request.get().json()
        )
        self.assertEqual({'1': 1}, data)

    @vcr.use_cassette()
    def test_get_raises_status_exception_correctly(self):
        self.assertRaises(HTTPError, self.client.get)


class TickerClientTestCase(TestCase):

    def setUp(self):
        self.client = TickerClient()

    def test_initializes_instance_correctly(self):
        self.assertIsInstance(self.client, BaseClient)
        self.assertEqual(DefaultParser, self.client.parser)
        self.assertEqual(RequestKwargsParser, self.client.KWARGS_CLASS)
        self.assertEqual('ticker/', self.client.PATH_URL)

    def test_initializes_instance_with_parser_correctly(self):
        client = TickerClient(3)
        self.assertEqual(3, client.parser)

    @vcr.use_cassette()
    def test_get_calls_kwargs_parser_correctly(self):
        mocked = Mock(RequestKwargsParser)
        mocked.parse.return_value = {'1': 1}
        self.client.KWARGS_CLASS = mocked

        self.client.get(1, 2, 3, 4)

        mocked.parse.assert_called_once_with(
            1, 2, 3, 4, SupportedFormats.LIST
        )

    @vcr.use_cassette()
    def test_client_get_do_request_to_api_correctly(self):
        data = self.client.get()

        self.assertIn('id', data[0])
        self.assertIn('name', data[0])
        self.assertIn('symbol', data[0])
        self.assertIn('rank', data[0])


class ListCryptoCoinClientTestCase(TestCase):

    def setUp(self):
        self.client = ListCryptoCoinClient()

    def test_initializes_instance_correctly(self):
        self.assertIsInstance(self.client, BaseClient)
        self.assertEqual(DefaultParser, self.client.parser)
        self.assertEqual('listings/', self.client.PATH_URL)

    def test_initializes_instance_with_parser_correctly(self):
        client = ListCryptoCoinClient(3)
        self.assertEqual(3, client.parser)

    @vcr.use_cassette()
    def test_list_client_get_do_request_to_api_correctly(self):
        data = self.client.get()

        self.assertIn('id', data[0])
        self.assertIn('name', data[0])
        self.assertIn('symbol', data[0])
        self.assertIn('website_slug', data[0])


class CryptoCoinTickerClientTestCase(TestCase):

    def setUp(self):
        self.client = CryptoCoinTickerClient()

    def test_initializes_instance_correctly(self):
        self.assertIsInstance(self.client, BaseClient)
        self.assertEqual(DefaultParser, self.client.parser)
        self.assertEqual(RequestKwargsParser, self.client.KWARGS_CLASS)
        self.assertEqual('ticker/', self.client.PATH_URL)

    def test_initializes_instance_with_parser_correctly(self):
        client = CryptoCoinTickerClient(3)
        self.assertEqual(3, client.parser)

    @vcr.use_cassette()
    def test_get_ticker_calls_kwargs_parser_correctly(self):
        mocked = Mock(RequestKwargsParser)
        mocked.parse.return_value = {'1': 1}
        self.client.KWARGS_CLASS = mocked

        self.client.get(1, 2)

        mocked.parse.assert_called_once_with(currency=2)

    @vcr.use_cassette()
    def test_client_get_ticker_do_request_to_api_correctly(self):
        data = self.client.get(1)

        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('symbol', data)
        self.assertIn('rank', data)

    @patch('coinmarketcap.clients.requests')
    def test_get_calls_request_correctly(self, m_request):
        self.client.parser = Mock()
        self.client.parser.parse.return_value = {'1': 1}

        data = self.client.get(1)

        expected_url = f'{self.client.url}1/'
        m_request.get.assert_called_once_with(expected_url, params={})
        self.client.parser.parse.assert_called_once_with(
            m_request.get().json()
        )
        self.assertEqual({'1': 1}, data)

    @vcr.use_cassette()
    def test_get_ticker_raises_status_exception_correctly(self):
        self.assertRaises(HTTPError, self.client.get, 'kkk')


class GlobalSummaryClientTestCase(TestCase):

    def setUp(self):
        self.client = GlobalSummaryClient()

    def test_initializes_instance_correctly(self):
        self.assertIsInstance(self.client, BaseClient)
        self.assertEqual(DefaultParser, self.client.parser)
        self.assertEqual(RequestKwargsParser, self.client.KWARGS_CLASS)
        self.assertEqual('global/', self.client.PATH_URL)

    def test_initializes_instance_with_parser_correctly(self):
        client = GlobalSummaryClient(3)
        self.assertEqual(3, client.parser)

    @vcr.use_cassette()
    def test_global_get_calls_kwargs_parser_correctly(self):
        mocked = Mock(RequestKwargsParser)
        mocked.parse.return_value = {'1': 1}
        self.client.KWARGS_CLASS = mocked

        self.client.get(1)

        mocked.parse.assert_called_once_with(currency=1)

    @vcr.use_cassette()
    def test_client_global_get_do_request_to_api_correctly(self):
        data = self.client.get()

        self.assertIn('active_cryptocurrencies', data)
        self.assertIn('active_markets', data)
        self.assertIn('bitcoin_percentage_of_market_cap', data)


class CoinMarketCapClientTestCase(TestCase):

    def setUp(self):
        self.client = CoinMarketCapClient()

    def test_initializes_instance_correctly(self):
        self.assertIsInstance(self.client.cryptocoin, CryptoCoinTickerClient)
        self.assertIsInstance(self.client.listing, ListCryptoCoinClient)
        self.assertIsInstance(self.client.tickers, TickerClient)
        self.assertIsInstance(self.client.global_data, GlobalSummaryClient)
