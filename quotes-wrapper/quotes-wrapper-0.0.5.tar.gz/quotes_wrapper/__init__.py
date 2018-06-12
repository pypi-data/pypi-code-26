import typing

import requests

from . import conf
from .exceptions import (QuoteNotFoundError, FetchingQuoteError,
                         UnknownConfigError, RequestTimeoutError)


def get_quotes() -> typing.Dict:
    try:
        resp = requests.get(conf.QUOTES_URL,
                            timeout=conf.QUOTES_REQUEST_TIMEOUT)

        if resp.status_code != requests.codes.ok:
            raise FetchingQuoteError
        return resp.json()

    except requests.Timeout:
        raise RequestTimeoutError


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
