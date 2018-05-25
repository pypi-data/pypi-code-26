# -*- coding: utf-8 -*-
"""
    zebe.service.app
    ~~~~~~~~~~~~~~~~

    应用相关的服务

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from zebe.modle.entity.app import App, AppModelSession
from zebe.service.base import ModelBaseService


# 应用服务
class AppService(ModelBaseService):
    def __init__(self):
        super().__init__(App, AppModelSession)

    # 通过名称查找一个应用
    def find_one_by_name(self, name):
        result = None
        if name is not None:
            result = self.session.query(self.entity).filter(self.entity.name == name).one_or_none()
            self.session.close()
        return result
