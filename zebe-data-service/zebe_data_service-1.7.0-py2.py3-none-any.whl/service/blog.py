# -*- coding: utf-8 -*-
"""
    zebe.service.blog
    ~~~~~~~~~~~~~~~~

    博客相关的服务

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from zebe.modle.entity.blog import ZebeBlogArticle, BlogModelSession, CdrVbaBlogArticle, CdrVbaBlogSubscriber
from zebe.service.base import ModelBaseService


# Zebe博客文章服务
class ZebeBlogArticleService(ModelBaseService):
    def __init__(self):
        super().__init__(ZebeBlogArticle, BlogModelSession)


# CorelDrawVBA博客文章服务
class CdrVbaBlogArticleService(ModelBaseService):
    def __init__(self):
        super().__init__(CdrVbaBlogArticle, BlogModelSession)


# CorelDrawVBA博客订阅者服务
class CdrVbaBlogSubscriberService(ModelBaseService):
    def __init__(self):
        super().__init__(CdrVbaBlogSubscriber, BlogModelSession)

    # 通过邮箱查找一个订阅者
    def find_one_by_email(self, email):
        result = None
        if email is not None:
            result = self.session.query(self.entity).filter(self.entity.email == email).one_or_none()
            self.session.close()
        return result
