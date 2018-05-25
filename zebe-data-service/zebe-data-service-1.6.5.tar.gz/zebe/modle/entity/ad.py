# -*- coding: utf-8 -*-
"""
    zebe.model.entity.ad
    ~~~~~~~~~~~~~~~~~~~~

    广告相关的实体类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, SmallInteger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.config.db import AD_DB

engine = create_engine('sqlite:///' + AD_DB, echo=True)
ModelBase = declarative_base()


# 广告
class Ad(ModelBase):
    __tablename__ = 'ad'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    name = Column(String(40), default="", nullable=False)  # 广告名称
    image = Column(String(300), default="", nullable=False)  # 广告图片
    link = Column(String(300), default="", nullable=False)  # 跳转链接
    is_enable = Column(SmallInteger, default=0, nullable=False, index=True)  # 是否有效（0=否 1=是）
    click_count = Column(Integer)  # 点击次数
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间

    def __repr__(self):
        return "<%s(name='%s')>" % (self.__class__.name, self.name)


ModelBase.metadata.create_all(engine)
AdModelSession = sessionmaker(bind=engine)
