from typing import List, Any, Iterator, Dict
import logging
from datetime import datetime
from urllib.parse import urljoin
from functools import partial

from ..core import (
    AbstractSyncRegisterStrategy, AbstractAsyncRegisterStrategy,
    AbstractAsyncExecutor, AbstractSyncExecutor, AbstractQueryParser, AbstractBackendAdapter
)

from .executor import CouchDBAsyncExecutor, CouchDBSyncExecutor
from .parser import CouchDBQueryParser
from .utils import parse_couchdb_connection_uri, DDOC_FOR_GENERATED_VIEWS_NAME

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["SyncCouchDBRegisterStrategy", "AsyncCouchDBRegisterStrategy", "CouchDBBackendAdapter"]

_log = logging.getLogger(__name__)
DDOC_INDEX_NAME_PREFIX = 'anji_orm_'
CORE_COUCHDB_METHODS = ()


class CouchDBRequestException(Exception):

    def __init__(self, query, content, status_code) -> None:
        super().__init__()
        self.query = query
        self.content = content
        self.status_code = status_code

    def __str__(self):
        return (
            f"Exception when executing query {str(self.query)}:\n"
            f"Response:{self.content}\n"
            f"Status code: {self.status_code}"
        )


def _ddoc_by_index(index_name: str) -> str:
    return f"{DDOC_INDEX_NAME_PREFIX}{index_name}"


def _controlled_index_filter(index_list: List[Dict]) -> Iterator[Dict]:
    return filter(
        lambda x: x['ddoc'] is not None and DDOC_INDEX_NAME_PREFIX in x["ddoc"],
        index_list
    )


def _build_primary_index_view() -> Dict:
    return {
        "language": "query",
        "views": {
            "count": {
                "map": {
                    "fields": {"_id": "asc"},
                    "partial_filter_selector": {}
                },
                "reduce": "_count",
                "options": {"def": {"fields": ["_id"]}}
            },
        }
    }


def _controlled_index_map(index_list: List[Dict]) -> Iterator[str]:
    return map(lambda x: x["name"], _controlled_index_filter(index_list))


class CouchDBBackendAdapter(AbstractBackendAdapter):

    def utcnow(self) -> datetime:
        return datetime.utcnow()

    def now(self) -> datetime:
        return datetime.now()

    def ensure_datetime_compatibility(self, value: datetime) -> datetime:
        return value

    def ensure_compatibility(self, value):
        return value


class SyncCouchDBRegisterStrategy(AbstractSyncRegisterStrategy):

    def __init__(self, connection_uri: str, **pool_kwargs: Any) -> None:  # pylint: disable=super-init-not-called
        import requests

        self.pool = requests.Session()
        settings = parse_couchdb_connection_uri(connection_uri)
        self.base_url = f"http://{settings.get('host', '127.0.0.1')}:{settings.get('port','5984')}"
        self.url_format = partial(urljoin, self.base_url)
        self._executor = CouchDBSyncExecutor(self)
        self._query_parser = CouchDBQueryParser()
        self._backend_adapter = CouchDBBackendAdapter()

    @property
    def executor(self) -> AbstractSyncExecutor:
        return self._executor

    @property
    def query_parser(self) -> AbstractQueryParser:
        return self._query_parser

    @property
    def backend_adapter(self) -> AbstractBackendAdapter:
        return self._backend_adapter

    def execute_query(self, query: Any) -> Any:
        query["url"] = self.url_format(query["url"])
        response = self.pool.request(**query)
        if response.ok:
            return response.json()
        raise CouchDBRequestException(
            query,
            response.json(),
            response.status_code
        )

    def load(self) -> None:
        pass

    def create_index(
            self, table_name: str,
            index_name: str, index_fields: List[str]) -> None:
        self.execute_query({
            "method": "post",
            "url": f"{table_name}/_index",
            "json": {
                "index": {
                    "fields": index_fields
                },
                "ddoc": _ddoc_by_index(index_name),
                "name": index_name
            }
        })

    def drop_index(self, table_name: str, index_name: str) -> None:
        self.execute_query({
            "method": "delete",
            "url": f"/{table_name}/_index/{_ddoc_by_index(index_name)}/json/{index_name}"
        })

    def list_indexes(self, table_name: str) -> List[str]:
        indexes = self.execute_query({
            "method": "get",
            "url": f"/{table_name}/_index"
        })["indexes"]
        return list(_controlled_index_map(indexes))

    def create_table(self, table_name: str) -> None:
        self.execute_query({
            "method": "put",
            "url": table_name
        })
        self.execute_query({
            "method": "put",
            "url": f"{table_name}/_design/{DDOC_FOR_GENERATED_VIEWS_NAME}",
            "json": {
                "language": "javascript",
                "views": {}
            }
        })

    def drop_table(self, table_name: str) -> None:
        self.execute_query({
            "method": "delete",
            "url": f'/{table_name}'
        })

    def list_tables(self) -> List[str]:
        return self.execute_query({
            "method": "get",
            "url": '_all_dbs'
        })

    def close(self) -> None:
        self.pool.close()


class AsyncCouchDBRegisterStrategy(AbstractAsyncRegisterStrategy):

    def __init__(self, connection_uri: str, **pool_kwargs: Any) -> None:  # pylint: disable=super-init-not-called
        import aiohttp

        self.pool: aiohttp.ClientSession
        settings = parse_couchdb_connection_uri(connection_uri)
        self.base_url = f"http://{settings.get('host', '127.0.0.1')}:{settings.get('port','5984')}"
        self.url_format = partial(urljoin, self.base_url)
        self._executor = CouchDBAsyncExecutor(self)
        self._query_parser = CouchDBQueryParser()
        self._backend_adapter = CouchDBBackendAdapter()

    @property
    def executor(self) -> AbstractAsyncExecutor:
        return self._executor

    @property
    def query_parser(self) -> AbstractQueryParser:
        return self._query_parser

    @property
    def backend_adapter(self) -> AbstractBackendAdapter:
        return self._backend_adapter

    async def execute_query(self, query: Any) -> Any:
        query["url"] = self.url_format(query["url"])
        response = await self.pool.request(**query)
        if response.status >= 200 and response.status < 400:
            return await response.json()
        raise CouchDBRequestException(
            query,
            await response.json(),
            response.status
        )

    async def load(self) -> None:
        import aiohttp

        self.pool = aiohttp.ClientSession()

    async def create_index(
            self, table_name: str,
            index_name: str, index_fields: List[str]) -> None:
        await self.execute_query({
            "method": "post",
            "url": f"{table_name}/_index",
            "json": {
                "index": {
                    "fields": index_fields
                },
                "ddoc": _ddoc_by_index(index_name),
                "name": index_name
            }
        })

    async def drop_index(self, table_name: str, index_name: str) -> None:
        await self.execute_query({
            "method": "delete",
            "url": f"/{table_name}/_index/{_ddoc_by_index(index_name)}/json/{index_name}"
        })

    async def list_indexes(self, table_name: str) -> List[str]:
        indexes = (await self.execute_query({
            "method": "get",
            "url": f"/{table_name}/_index"
        }))["indexes"]
        return list(_controlled_index_map(indexes))

    async def create_table(self, table_name: str) -> None:
        await self.execute_query({
            "method": "put",
            "url": table_name
        })
        await self.execute_query({
            "method": "put",
            "url": f"{table_name}/_design/{DDOC_FOR_GENERATED_VIEWS_NAME}",
            "json": {
                "language": "javascript",
                "views": {}
            }
        })

    async def drop_table(self, table_name: str) -> None:
        await self.execute_query({
            "method": "delete",
            "url": f'/{table_name}'
        })

    async def list_tables(self) -> List[str]:
        return await self.execute_query({
            "method": "get",
            "url": '_all_dbs'
        })

    async def close(self) -> None:
        await self.pool.close()
