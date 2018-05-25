# -*- coding: utf-8 -*-
"""
    zebe.service.ad
    ~~~~~~~~~~~~~~~~

    广告相关的服务

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from zebe.modle.entity.ad import Ad, AdModelSession
from zebe.service.base import ModelBaseService


# 广告服务
class AdService(ModelBaseService):
    def __init__(self):
        super().__init__(Ad, AdModelSession)
