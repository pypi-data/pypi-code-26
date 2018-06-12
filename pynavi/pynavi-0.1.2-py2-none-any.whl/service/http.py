# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)

import json as jsonlib

from requests import request

from pynavi.service import BaseService
from pynavi.view.request import M


class HttpBaseService(BaseService):
    """http访问基类"""

    def __init__(self, host, port, method=M.POST, timeout=3, retry_times=0, headers=None):
        super(HttpBaseService, self).__init__()

        self._host = host
        self._port = port
        self._http_method = method
        self._headers = headers
        self._timeout = timeout
        self._retry_times = retry_times

    def request(self, uri, http_method=None, **kws):
        if not http_method:
            http_method = self._http_method

        if http_method == M.GET:
            kws.setdefault('allow_redirects', True)

        if self._headers:
            if 'headers' not in kws or kws['headers'] is None:
                kws['headers'] = {}

            kws['headers'].update(self._headers)

        if self._port:
            url = 'http://{}:{}/{}'.format(self._host, self._port, uri.lstrip('/'))
        else:
            url = 'http://{}/{}'.format(self._host, uri.lstrip('/'))

        r = request(http_method.lower(), url, **kws)

        return r.text


class JsonHttpBaseService(HttpBaseService):
    """返回格式为json格式的接口基类"""

    def __init__(self, host, port, headers):
        super(JsonHttpBaseService, self).__init__(host=host, port=port, headers=headers)

    def request(self, uri, headers=None, http_method=None, json=None, data=None, **kws):
        r = super(JsonHttpBaseService, self).request(uri=uri, headers=headers, http_method=http_method, json=json, data=data, **kws)
        return jsonlib.loads(r)
