#!/usr/bin/python
# -*- coding: UTF-8 -*-
r"""
@author: Martin Klapproth <martin.klapproth@googlemail.com>
"""

import logging

logger = logging.getLogger(__name__)

class RemoteException(Exception):
    def __init__(self, msg=""):
        self.msg = msg
    def __str__(self):
        r = self.__class__.__name__
        if self.msg:
            r += ": " + self.msg
        return r

class AuthenticationFailedException(RemoteException):
    pass

class NetworkException(RemoteException):
    pass
