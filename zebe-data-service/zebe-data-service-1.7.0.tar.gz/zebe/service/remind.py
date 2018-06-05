# -*- coding: utf-8 -*-
"""
    zebe.service.remind
    ~~~~~~~~~~~~~~~~

    提醒相关的服务

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""
from zebe.modle.entity.remind import Remind, RemindModelSession
from zebe.service.base import ModelBaseService


# 提醒服务
class RemindService(ModelBaseService):
    def __init__(self):
        super().__init__(Remind, RemindModelSession)

    # 按照模式查询项目
    def find_by_mode(self, mode):
        result = self.session.query(self.entity).filter(self.entity.mode == mode).all()
        self.session.close()
        return result
