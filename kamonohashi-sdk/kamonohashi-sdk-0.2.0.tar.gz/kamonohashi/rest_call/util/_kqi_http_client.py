# -*- coding: utf-8 -*-
# Copyright 2018 NS Solutions Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
manage REST API for KQI REST API.
"""
from __future__ import print_function, absolute_import, unicode_literals, with_statement
import json

from kamonohashi.rest_call.util._kqi_auth import TokenAuth
from kamonohashi.util._module_logger import get_logger
from kamonohashi.util._encoder import resolve_encode
from kamonohashi.util._http_client import HttpClient


class RestCallError(Exception):
    def __init__(self, raw_response):
        self.status_code = raw_response.status_code
        self.reason = raw_response.reason
        self.api_url = raw_response.url
        self.content = raw_response.content
        self.response = raw_response


class KqiHttpClient(HttpClient):
    def __init__(self, server, token, timeout=60, retry=5):
        """Constructor

        Args:
            server (str): Server ip
            token (str): Token from ap server
            timeout (int): Receive timeout
        """
        self.logger = get_logger(__name__)

        # get from config file
        self.server = self.__correctly_url(server)
        self.token = token

        super(KqiHttpClient, self).__init__(timeout=timeout, retry=retry)

    def api_post(self, api, data=None, as_json=False):
        """Post method"""
        url = self.__correct_api_path(api)
        if data is not None:
            data = json.dumps(data) if as_json else data
        headers = {'content-type': 'application/json'} if as_json else None
        response = self.post(url=url,
                             data=data,
                             headers=headers,
                             auth=TokenAuth(self.token))
        self.__is_success(response)
        return response

    def api_get(self, api, stream=False, params=None):
        """Get method"""
        url = self.__correct_api_path(api)
        response = self.get(url=url,
                            stream=stream,
                            params=params,
                            auth=TokenAuth(self.token))
        self.__is_success(response)
        return response

    def api_delete(self, api):
        """Delete method"""
        url = self.__correct_api_path(api)
        response = self.delete(url=url,
                               auth=TokenAuth(self.token))
        self.__is_success(response)
        return response

    def api_put(self, api, data, as_json=False):
        """Put method"""
        url = self.__correct_api_path(api)
        data = json.dumps(data) if as_json else data
        headers = {'content-type': 'application/json'} if as_json else None
        response = self.put(url=url,
                            data=data,
                            headers=headers,
                            auth=TokenAuth(self.token))
        self.__is_success(response)
        return response

    def api_patch(self, api, data, as_json):
        """Patch method"""
        url = self.__correct_api_path(api)
        data = json.dumps(data) if as_json else data
        headers = {'content-type': 'application/json'} if as_json else None
        response = self.patch(url=url,
                              data=data,
                              headers=headers,
                              auth=TokenAuth(self.token))
        self.__is_success(response)
        return response

    def __is_success(self, response):
        status_code = response.status_code
        method = response.request.method
        url = response.request.url

        if 200 <= status_code <= 299:
            self.logger.debug('{method} to {url} success: {message}'.format(method=method, url=url, message=status_code))
            return

        # failed status code
        content = resolve_encode(response.content)
        if 400 <= status_code <= 499:
            self.logger.error('{method} Client Error: {url} {message} -> Exit process'.format(method=method, url=url, message=content))
        elif 500 <= status_code <= 599:
            self.logger.error('{method} Server Error: {url} {message} -> Exit process'.format(method=method, url=url, message=content))
        raise RestCallError(response)

    def __correct_api_path(self, api):
        api = api if api.startswith('/') else '/' + api
        url = self.server + api
        self.logger.debug('connecting to {url}'.format(url=url))
        return url

    @staticmethod
    def __correctly_url(url):
        return url[:-1] if url[-1].endswith('/') else url
