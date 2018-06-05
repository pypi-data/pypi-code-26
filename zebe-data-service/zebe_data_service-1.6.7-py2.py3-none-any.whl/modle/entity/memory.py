# -*- coding: utf-8 -*-
"""
    zebe.model.entity.memory
    ~~~~~~~~~~~~~~~~~~~~~~~

    记忆相关的实体类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Text, SmallInteger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.config.db import MEMORY_DB

engine = create_engine('sqlite:///' + MEMORY_DB, echo=True)
MemoryModelBase = declarative_base()


# 数字编码
class NumberCode(MemoryModelBase):
    __tablename__ = 'number_code'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    number = Column(String(3), default="", nullable=False, index=True)  # 数字
    code = Column(String(10), default="", nullable=False)  # 编码
    image = Column(String(300), default="", nullable=False)  # 图像
    version = Column(Integer, default=0, nullable=False)  # 版本
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间

    def __repr__(self):
        return "<%s(number='%s')>" % (self.__class__.name, self.number)


MemoryModelBase.metadata.create_all(engine)
MemoryModelModelSession = sessionmaker(bind=engine)
