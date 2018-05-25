# -*- coding: utf-8 -*-
"""
    zebe.model.entity.wechat
    ~~~~~~~~~~~~~~~~

    微信相关的实体类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.config.db import WECHAT_DB

engine = create_engine('sqlite:///' + WECHAT_DB, echo=True)
WeChatModelBase = declarative_base()


# 秒记先生微信用户
class WeChatMiaoJiUser(WeChatModelBase):
    __tablename__ = 'wechat_miaoji_user'
    id = Column(String(28), primary_key=True)  # ID（和openId相同）
    realname = Column(String(20), nullable=False, default='')  # 真实姓名
    nickname = Column(String(32), nullable=False, default='')  # 昵称
    wxid = Column(String(20), nullable=False, default='')  # 微信号
    follow_time = Column(DateTime, nullable=False, default=datetime.now())  # 关注时间
    unfollow_time = Column(DateTime)  # 取消关注时间

    def __repr__(self):
        return "<%s(id='%s')>" % (self.__class__.name, self.id)


# 秒记先生微信用户发来的消息
class WeChatMiaoJiUserMessage(WeChatModelBase):
    __tablename__ = 'wechat_miaoji_user_msg'
    id = Column(Integer, primary_key=True)  # ID
    type = Column(String(10), default="", nullable=False, index=True)  # 消息类型
    content = Column(Text, default="", nullable=False)  # 文本内容
    voice = Column(Text, default="", nullable=False)  # 语音内容
    link = Column(String(300), default="", nullable=False)  # 链接
    source = Column(String(40), default="", nullable=False)  # 消息来源
    reply = Column(Text, default="", nullable=False)  # 回复内容
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 发送时间

    def __repr__(self):
        return "<%s(content='%s')>" % (self.__class__.name, self.content)


# Zebe个人微信用户
class WeChatZebeUser(WeChatModelBase):
    __tablename__ = 'wechat_zebe_user'
    id = Column(String(28), primary_key=True)  # ID（和openId相同）
    realname = Column(String(20), nullable=False, default='')  # 真实姓名
    nickname = Column(String(32), nullable=False, default='')  # 昵称
    wxid = Column(String(20), nullable=False, default='')  # 微信号
    follow_time = Column(DateTime, nullable=False, default=datetime.now())  # 关注时间
    unfollow_time = Column(DateTime)  # 取消关注时间

    def __repr__(self):
        return "<%s(id='%s')>" % (self.__class__.name, self.id)


# Zebe个人微信用户发来的消息
class WeChatZebeUserMessage(WeChatModelBase):
    __tablename__ = 'wechat_zebe_user_msg'
    id = Column(Integer, primary_key=True)  # ID
    type = Column(String(10), default="", nullable=False, index=True)  # 消息类型
    content = Column(Text, default="", nullable=False)  # 文本内容
    voice = Column(Text, default="", nullable=False)  # 语音内容
    link = Column(String(300), default="", nullable=False)  # 链接
    source = Column(String(40), default="", nullable=False)  # 消息来源
    reply = Column(Text, default="", nullable=False)  # 回复内容
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 发送时间

    def __repr__(self):
        return "<%s(content='%s')>" % (self.__class__.name, self.content)


WeChatModelBase.metadata.create_all(engine)
WechatModelSession = sessionmaker(bind=engine)
