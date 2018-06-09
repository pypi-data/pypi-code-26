import requests
from abc import ABC

from coinmarketcap.constants import SupportedFormats
from coinmarketcap.parsers import DefaultParser, RequestKwargsParser


class BaseClient(ABC):

    BASE_URL = 'https://api.coinmarketcap.com/v2/'
    PATH_URL = ''

    @property
    def url(self):
        return f'{self.BASE_URL}{self.PATH_URL}'

    def get(self, **kwargs):
        response = requests.get(self.url, params=kwargs)
        response.raise_for_status()

        data = response.json()
        return self.parser.parse(response.json())


class TickerClient(BaseClient):

    PATH_URL = 'ticker/'
    KWARGS_CLASS = RequestKwargsParser

    def __init__(self, parser=None):
        self.parser = parser or DefaultParser

    def get(self, start=0, limit=0, sort=None, currency=None):
        kwargs = self.KWARGS_CLASS.parse(start, limit, sort, currency, SupportedFormats.LIST)
        return super().get(**kwargs)


class ListCryptoCoinClient(BaseClient):

    PATH_URL = 'listings/'

    def __init__(self, parser=None):
        self.parser = parser or DefaultParser

    def get(self):
        return super().get()


class CryptoCoinTickerClient(BaseClient):

    PATH_URL = 'ticker/'
    KWARGS_CLASS = RequestKwargsParser

    def __init__(self, parser=None):
        self.parser = parser or DefaultParser

    def get(self, coin_id, currency=None):
        url = f'{self.url}{coin_id}/'
        kwargs = self.KWARGS_CLASS.parse(currency=currency)

        response = requests.get(url, params=kwargs)
        response.raise_for_status()

        data = response.json()
        return self.parser.parse(response.json())


class GlobalSummaryClient(BaseClient):

    PATH_URL = 'global/'
    KWARGS_CLASS = RequestKwargsParser

    def __init__(self, parser=None):
        self.parser = parser or DefaultParser

    def get(self, currency=None):
        kwargs = self.KWARGS_CLASS.parse(currency=currency)
        return super().get(**kwargs)


class CoinMarketCapClient:

    def __init__(self):
        self.cryptocoin = CryptoCoinTickerClient()
        self.listing = ListCryptoCoinClient()
        self.tickers = TickerClient()
        self.global_data = GlobalSummaryClient()
