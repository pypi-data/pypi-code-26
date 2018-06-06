from typing import Dict
from urllib.parse import urlparse
from datetime import datetime

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["parse_couchdb_connection_uri", "serialize_datetime", "deserialize_datetime"]

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
DDOC_FOR_GENERATED_VIEWS_NAME = "anji_orm_generated_views_ddoc"
CONNECTION_URI_MAPPING = {
    'hostname': 'host',
    'port': 'port',
    'username': 'user',
    'password': 'password',
}


def parse_couchdb_connection_uri(connection_uri: str) -> Dict:
    parsed_url = urlparse(connection_uri)
    connection_kwargs = {}
    for uri_field, connection_arg in CONNECTION_URI_MAPPING.items():
        if getattr(parsed_url, uri_field):
            connection_kwargs[connection_arg] = getattr(parsed_url, uri_field)
    if parsed_url.query:
        connection_kwargs.update({
            x[0]: x[1] for x in (x.split('=') for x in parsed_url.query.split('&'))
        })
    return connection_kwargs


def serialize_datetime(value: datetime) -> str:
    return value.strftime(DATETIME_FORMAT)


def deserialize_datetime(value: str) -> datetime:
    return datetime.strptime(value, DATETIME_FORMAT)
