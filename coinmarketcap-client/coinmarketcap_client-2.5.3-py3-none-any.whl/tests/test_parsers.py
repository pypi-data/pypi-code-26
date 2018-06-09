from unittest import TestCase

from coinmarketcap.constants import Currencies, SortBy, SupportedFormats
from coinmarketcap.exceptions import SortValueError, CurrencyValueError
from coinmarketcap.parsers import DefaultParser, RequestKwargsParser


class RequestKwargsParserTestCase(TestCase):

    def setUp(self):
        self.parser = RequestKwargsParser
        self.kwargs = {
            'start': 1,
            'limit': 2,
            'sort': SortBy.RANK,
            'currency': Currencies.BRL,
            'structure': SupportedFormats.LIST,
        }

    def test_parse_correct_data(self):
        data = self.parser.parse({})
        self.assertEqual({}, data)

    def test_parse_correct_data_with_params(self):
        data = self.parser.parse(**self.kwargs)

        self.assertEqual(SupportedFormats.LIST, data['structure'])
        self.assertEqual(1, data['start'])
        self.assertEqual(2, data['limit'])
        self.assertEqual(SortBy.RANK, data['sort'])
        self.assertEqual(Currencies.BRL, data['convert'])

    def test_parse_raises_exception_for_unsupported_sort_param(self):
        self.assertRaises(SortValueError, self.parser.parse, sort='awb')

    def test_parse_raises_exception_for_unsupported_currency_param(self):
        self.assertRaises(SortValueError, self.parser.parse, sort='awb')


class DefaultParserTestCase(TestCase):

    def setUp(self):
        self.parser = DefaultParser
        self.data = {'data': [1, 2]}

    def test_parse_correct_data(self):
        parsed = self.parser.parse(self.data)
        self.assertEqual([1, 2], parsed)
