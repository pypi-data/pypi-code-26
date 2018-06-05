# -*- coding: utf-8 -*-
"""
    zebe.model.entity.cdrvba
    ~~~~~~~~~~~~~~~~~~~~~~~

    CorelDrawVBA相关的实体类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.config.db import CDRVBA_DB

engine = create_engine('sqlite:///' + CDRVBA_DB, echo=True)
CorelDrawVBAModelBase = declarative_base()


# CorelDrawVBA文章
class CorelDrawVBAArticle(CorelDrawVBAModelBase):
    __tablename__ = 'cdrvba_article'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    title = Column(String(50), default="", nullable=False)  # 标题
    summary = Column(String(150), default="", nullable=False)  # 摘要
    content = Column(Text, default="", nullable=False)  # 内容
    type = Column(String(10), default="", nullable=False, index=True)  # 分类
    tags = Column(String(100), default="", nullable=False)  # 标签
    cover = Column(String(300), default="", nullable=False)  # 封面图
    view_count = Column(Integer, default=0, nullable=False)  # 浏览数
    comment_count = Column(Integer, default=0, nullable=False)  # 评论数
    link = Column(String(300), default="", nullable=False, index=True)  # 链接
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间


CorelDrawVBAModelBase.metadata.create_all(engine)
CorelDrawVBAModelSession = sessionmaker(bind=engine)
