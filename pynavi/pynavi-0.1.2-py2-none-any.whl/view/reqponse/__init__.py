# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)
from collections import OrderedDict

from django.http import JsonResponse


class ErrorCode(object):
    """系统错误码定义"""

    def __init__(self, code, http_code, message_en='', message_cn='', **kwargs):
        self._code = code
        self._http_code = http_code
        self._message_en = message_en
        self._message_cn = message_cn
        self._ext = kwargs

    @property
    def code(self):
        return self._code

    @property
    def http_code(self):
        return self._http_code

    @property
    def message_en(self):
        return self._message_en

    def message(self, message=None):
        if message is None:
            return self._message_en

        self._message_en = message

        return self

    @property
    def message_cn(self):
        return self._message_cn

    @property
    def ext(self):
        return self._ext

    @classmethod
    def custom_error(cls, message_en='', message_cn=''):
        return ErrorCode(code=CUSTOMER_ERROR.code, http_code=CUSTOMER_ERROR.http_code, message_en=message_en, message_cn=message_cn)


E = ErrorCode


class NaviJsonResponse(JsonResponse):
    """
    pynavi json http response
    pynavi response 返回协议格式：
    {
        'code': 1,
        'message': 'success',
        'data': {
            *****
        },
        'cost': 0.003
    }
    """

    def __init__(self, data=None, ext=None, **kws):
        if data is None:
            data = {}

        # pynavi 返回协议格式
        resp = OrderedDict({
            'code'   : kws.pop('code') if 'code' in kws else 0,
            'message': kws.pop('message') if 'message' in kws else '',
            'data'   : data
        })

        if ext:
            for k, v in ext.items():
                resp.update({k: v})

        super(NaviJsonResponse, self).__init__(resp, **kws)


# NAVI 系统定义错误码
SYSTEM_ERROR = E(code=-1, http_code=200, message_en='system error', message_cn='系统错误')

ACTION_SUCCESS = E(code=0, http_code=200, message_en='action success')
ACTION_FAIL = E(code=1, http_code=200, message_en='action failed')
AUTH_ERROR = E(code=2, http_code=200, message_en='auth error', message_cn='参数错误')
PARAM_ERROR = E(code=3, http_code=200, message_en='param failed')

CUSTOMER_ERROR = E(code=4, http_code=200, message_en='customer error', message_cn='自定义错误')

# 数据类错误
NO_DATA_FOUND = E(code=102, http_code=200, message_en='no data found')

# DB 类错误
DB_ERROR = E(code=201, http_code=200, message_en='db access error')

# 缓存类错误
CACHE_ERROR = E(code=301, http_code=200, message_en='cache access error')
