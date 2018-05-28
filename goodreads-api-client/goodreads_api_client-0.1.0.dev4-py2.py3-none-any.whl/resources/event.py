# -*- coding: utf-8 -*-
"""Module containing event resource class."""

from goodreads_api_client.resources.base import Resource


class Event(Resource):
    resource_name = 'event'

    def list(self, lat: str, lng: str, country_code: str, postal_code: str):
        endpoint = 'event/index'
        params = {
            'lat': lat,
            'lng': lng,
            'search[country_code]': country_code,
            'search[postal_code]': postal_code,
        }
        res = self._transport.req(endpoint=endpoint, params=params)
        return res['events']
