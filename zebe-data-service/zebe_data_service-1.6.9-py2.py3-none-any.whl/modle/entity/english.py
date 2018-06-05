# -*- coding: utf-8 -*-
"""
    zebe.model.entity.english
    ~~~~~~~~~~~~~~~~~~~~~

    英语相关的实体类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from sqlalchemy import Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.config.db import ENGLISH_DB

engine = create_engine('sqlite:///' + ENGLISH_DB, echo=True)
ModelBase = declarative_base()


# 英语短语
class EnglishPhrase(ModelBase):
    __tablename__ = 'english_phrase'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    first_letter = Column(String(1), default="", nullable=False, index=True)  # 首字母
    word = Column(String(30), default="", nullable=False)  # 单词
    description = Column(String(50), default="", nullable=False)  # 含义
    demo = Column(String(100), default="", nullable=False)  # 例句

    def __repr__(self):
        return "<%s(name='%s')>" % (self.__class__.name, self.name)


ModelBase.metadata.create_all(engine)
EnglishModelSession = sessionmaker(bind=engine)
