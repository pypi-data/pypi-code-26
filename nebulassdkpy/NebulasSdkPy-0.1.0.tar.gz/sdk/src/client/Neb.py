# -*- coding: utf-8 -*-
# @Time    : 2018/6/3 下午9:27
# @Author  : GuoXiaoMin
# @File    : Neb.py
# @Software: PyCharm
from sdk.src.client.Api import Api
from sdk.src.client.Admin import Admin


class Neb:

    def __init__(self):
        self.api = Api()
        self.admin = Admin()

    def set_request(self):
        self.api.set_request()
        self.admin.set_request()

