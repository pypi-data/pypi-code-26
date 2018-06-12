# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)

from enum import Enum


class _RequestMethod(object):

    def __init__(self):
        pass

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    HEAD = 'HEAD'
    TRACE = 'TRACE'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'


M = _RequestMethod


class RequestParamType(Enum):
    str = 0
    string = 0
    int = 1
    float = 2
    str_list = 3
    string_list = 3
    int_list = 4
    float_list = 5
    json = 6
    file = 7
    datetime = 8


PType = RequestParamType
