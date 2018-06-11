import typing

import requests
from . import conf
from .exceptions import (QuoteNotFoundError, FetchingQuoteError,
                         UnknownConfigError)

__version__ = '0.0.2'


def get_quotes() -> typing.Dict:
    resp = requests.get(conf.QUOTES_URL)

    if resp.status_code != requests.codes.ok:
        raise FetchingQuoteError
    return resp.json()


def get_quote(number: int) -> typing.Dict[str, typing.List]:
    try:
        quote = get_quotes()['quotes'][number]
        return {'quote': [quote]}
    except IndexError:
        raise QuoteNotFoundError


def configure(key: str, value: typing.Any) -> None:
    if not hasattr(conf, key):
        raise UnknownConfigError

    setattr(conf, key, value)
