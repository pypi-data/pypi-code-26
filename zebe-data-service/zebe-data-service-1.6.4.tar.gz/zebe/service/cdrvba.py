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