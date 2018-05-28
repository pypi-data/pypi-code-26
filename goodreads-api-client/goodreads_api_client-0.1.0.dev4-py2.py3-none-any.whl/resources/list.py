# -*- coding: utf-8 -*-
"""Module containing list resource class."""

from goodreads_api_client.exceptions import ExtraApiPermissionsRequired
from goodreads_api_client.resources.base import Resource


class List(Resource):
    def show(self, id_: str):
        raise ExtraApiPermissionsRequired('list.show')
