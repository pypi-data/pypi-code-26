# -*- coding: utf-8 -*-
"""
    zebe.service.memcard
    ~~~~~~~~~~~~~~~~

    秒记卡相关的服务

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from sqlalchemy import distinct

from zebe.modle.entity.memcard import MemoryCard, MemoryCardModelSession
from zebe.service.base import ModelBaseService


# 秒记卡服务
class MemoryCardService(ModelBaseService):

    def __init__(self):
        super().__init__(MemoryCard, MemoryCardModelSession)

    # 按分类统计
    def count_all_by_type(self, type_name):
        result = self.session.query(self.entity).filter(self.entity.type == type_name).count()
        self.session.close()
        return result

    # 查询所有分类
    def find_all_types(self):
        result = self.session.query(distinct(self.entity.type)).all()
        self.session.close()
        types = []
        for r in result:
            types.append(r[0])
        return types

    # 通过类型查询
    def find_by_type(self, type_name):
        result = self.session.query(self.entity).filter(self.entity.type == type_name).all()
        self.session.close()
        return result

    # 通过key查询单张秒记卡
    def find_one_by_key(self, key):
        result = self.session.query(self.entity).filter(self.entity.key == key).one_or_none()
        self.session.close()
        return result
