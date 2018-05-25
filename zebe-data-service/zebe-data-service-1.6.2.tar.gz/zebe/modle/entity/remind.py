# -*- coding: utf-8 -*-
"""
    zebe.model.entity.remind
    ~~~~~~~~~~~~~~~~~~~~~~~~

    提醒相关的实体类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from datetime import datetime

from sqlalchemy import Column, String, Integer, Text, DateTime, SmallInteger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.config.db import REMIND_DB

engine = create_engine('sqlite:///' + REMIND_DB, echo=True)
RemindModelBase = declarative_base()


# 提醒
class Remind(RemindModelBase):
    __tablename__ = 'remind'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    title = Column(String(40), default="", nullable=False)  # 提醒标题
    content = Column(Text, default="", nullable=False)  # 提醒内容
    sound = Column(String(300), default="", nullable=False)  # 提醒声音
    mode = Column(String(8), default='', nullable=False, index=True)  # 模式（CRON表达式=cron，周期间隔=interval）
    cron_day_of_week = Column(String(30), default='', nullable=False)  # CRON周表达式
    cron_hour = Column(String(30), default='', nullable=False)  # CRON小时表达式
    cron_minute = Column(String(30), default='', nullable=False)  # CRON分钟表达式
    cron_second = Column(String(30), default='', nullable=False)  # CRON秒表达式
    receiver_email = Column(Text, default="", nullable=False)  # 接收者邮箱
    receiver_phone = Column(Text, default="", nullable=False)  # 接收者电话
    receiver_wechat = Column(Text, default="", nullable=False)  # 接收者微信
    is_enable = Column(SmallInteger, default=0, nullable=False, index=True)  # 是否有效（0=否 1=是）
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间
    last_trigger_time = Column(DateTime)  # 最后触发时间
    finish_time = Column(DateTime)  # 完成时间

    def __repr__(self):
        return "<%s(title='%s')>" % (self.__class__.name, self.title)


RemindModelBase.metadata.create_all(engine)
RemindModelSession = sessionmaker(bind=engine)
