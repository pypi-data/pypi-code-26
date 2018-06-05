# -*- coding: utf-8 -*-
"""
    zebe.service.cdrvba
    ~~~~~~~~~~~~~~~~

    CorelDrawVBA相关的服务

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from zebe.modle.entity.cdrvba import CorelDrawVBAArticle, CorelDrawVBAModelSession

from zebe.service.base import ModelBaseService


# CorelDrawVBA文章服务
class CorelDrawVBAArticleService(ModelBaseService):
    def __init__(self):
        super().__init__(CorelDrawVBAArticle, CorelDrawVBAModelSession)

    # 查询全部数据并按照日期倒序排列
    def find_all_ordered_by_time(self):
        result = self.session.query(self.entity).order_by(self.entity.create_time.desc()).all()
        self.session.close()
        return result

    # 查询指定类型的数据并按照日期倒序排列
    def find_all_by_type(self, data_type):
        result = self.session.query(self.entity).filter(self.entity.type == data_type).order_by(self.entity.create_time.desc()).all()
        self.session.close()
        return result

    # 查询指定标签的数据并按照日期倒序排列
    def find_all_by_tag(self, tag):
        result = self.session.query(self.entity).filter(self.entity.tags.like(tag + "%")).order_by(
            self.entity.create_time.desc()).all()
        self.session.close()
        return result
