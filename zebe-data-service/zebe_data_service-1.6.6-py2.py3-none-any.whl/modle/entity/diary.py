# -*- coding: utf-8 -*-
"""
    zebe.model.entity.diary
    ~~~~~~~~~~~~~~~~~~~~~~~

    日记相关的实体类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Text, SmallInteger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.config.db import DIARY_DB

engine = create_engine('sqlite:///' + DIARY_DB, echo=True)
DiaryModelBase = declarative_base()


# 日记
class Diary(DiaryModelBase):
    __tablename__ = 'diary'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    title = Column(String(50), default="", nullable=False)  # 标题
    content = Column(Text, default="", nullable=False)  # 内容
    learned = Column(SmallInteger, default=0, nullable=False)  # 新掌握知识数量
    year = Column(SmallInteger, default=0, nullable=False, index=True)  # 所属年份
    month = Column(SmallInteger, default=0, nullable=False, index=True)  # 所属月份
    day = Column(SmallInteger, default=0, nullable=False, index=True)  # 所属日期
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间

    def __repr__(self):
        return "<%s(title='%s')>" % (self.__class__.name, self.title)


DiaryModelBase.metadata.create_all(engine)
DiaryModelSession = sessionmaker(bind=engine)
