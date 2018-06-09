from coinmarketcap.constants import Currencies, SortBy, SupportedFormats
from coinmarketcap.exceptions import SortValueError, CurrencyValueError


class DefaultParser:

    @classmethod
    def parse(cls, data):
        return data['data']


class NullableParser:

    @classmethod
    def parse(cls, data):
        return data


class RequestKwargsParser:

    @classmethod
    def parse(cls, start=0, limit=0, sort=None, currency=None, structure=None):
        kwargs = {}

        if structure:
            kwargs['structure'] = structure
        if start:
            kwargs['start'] = start
        if limit:
            kwargs['limit'] = limit
        if sort:
            if sort not in dict(SortBy.TYPES):
                raise SortValueError(f'Unsupported sort value. Expect values are {", ".join(dict(SortBy.TYPES).keys())}')
            kwargs['sort'] = sort
        if currency:
            if currency not in dict(Currencies.TYPES):
                raise CurrencyValueError(f'Unsupported sort value. Expect values are {", ".join(dict(SortBy.TYPES).keys())}')
            kwargs['convert'] = currency

        return kwargs
