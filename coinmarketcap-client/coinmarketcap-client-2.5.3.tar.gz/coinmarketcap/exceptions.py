from coinmarketcap.constants import Currencies, SortBy


class SortValueError(Exception):
    '''
        Exception to be raised when unsupported sort value was
        passed as param. See constants.SortBy
    '''


class CurrencyValueError(Exception):
    '''
        Exception to be raised when unsupported currency value
        was passed as param. See constants.Currencies
    '''
