# -*- coding: utf-8 -*-
"""
    zebe.service.wechat
    ~~~~~~~~~~~~~~~~

    微信相关的服务

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from zebe.modle.entity.wechat import WechatModelSession, WeChatMiaoJiUser, WeChatZebeUser, WeChatMiaoJiUserMessage, \
    WeChatZebeUserMessage
from zebe.service.base import ModelBaseService


# 秒记先生微信用户服务
class WeChatMiaoJiUserService(ModelBaseService):
    def __init__(self):
        super().__init__(WeChatMiaoJiUser, WechatModelSession)


# 秒记先生微信用户消息服务
class WeChatMiaoJiUserMessageService(ModelBaseService):
    def __init__(self):
        super().__init__(WeChatMiaoJiUserMessage, WechatModelSession)


# Zebe个人微信用户服务
class WeChatZebeUserService(ModelBaseService):
    def __init__(self):
        super().__init__(WeChatZebeUser, WechatModelSession)


# Zebe个人微信用户消息服务
class WeChatZebeUserMessageService(ModelBaseService):
    def __init__(self):
        super().__init__(WeChatZebeUserMessage, WechatModelSession)
