# -*- coding: utf-8 -*-
"""Module containing book resource class."""

from typing import Iterable
from goodreads_api_client.resources.base import Resource


class Book(Resource):
    resource_name = 'book'

    def id_to_work_id(self, ids: Iterable[str]):
        id_csv = ','.join(ids)
        endpoint = 'book/id_to_work_id/{}'.format(id_csv)
        res = self._transport.req(endpoint=endpoint)
        return res['work-ids']

    def isbn_to_id(self, isbns: Iterable[str]):
        raise NotImplementedError('API always 404s on this endpoint')

    def review_counts(self, isbns: Iterable[str]):
        # This endpoint 406s on non-json content type
        endpoint = 'book/review_counts.json'
        params = {
            'isbns': ','.join(set(isbns)),
        }
        res = self._transport.req(endpoint=endpoint, params=params,
                                  transform='json')
        return res['books']

    def show(self, id_: str):
        return self._show_single_resource(id_)

    def show_by_isbn(self, isbn: str):
        endpoint = 'book/isbn/{}'.format(isbn)
        res = self._transport.req(endpoint=endpoint)
        return res['book']

    def title(self, title: str, author: str=None, rating: int=None):
        endpoint = 'book/title'
        params = {
            'author': author,
            'rating': rating,
            'title': title,
        }
        res = self._transport.req(endpoint=endpoint, params=params)
        return res['book']
