# -*- coding: utf-8 -*-

class HaobtcOauthError(Exception):

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "Error! code: %d, message: %s" % (self.code, self.msg)
