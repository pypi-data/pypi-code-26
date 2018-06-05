# -*- coding: utf-8 -*-
"""
    zebe.model.entity.blog
    ~~~~~~~~~~~~~~~~~~~~~~

    博客相关的实体类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.config.db import BLOG_DB

engine = create_engine('sqlite:///' + BLOG_DB, echo=True)
BlogModelBase = declarative_base()


# Zebe博客文章
class ZebeBlogArticle(BlogModelBase):
    __tablename__ = 'zebe_blog_article'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    title = Column(String(50), default="", nullable=False)  # 标题
    content = Column(Text, default="", nullable=False)  # 内容
    type = Column(String(10), default="", nullable=False)  # 分类
    tags = Column(String(100), default="", nullable=False)  # 标签
    cover = Column(String(300), default="", nullable=False)  # 封面图
    view_count = Column(Integer, default=0, nullable=False)  # 浏览数
    comment_count = Column(Integer, default=0, nullable=False)  # 评论数
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间

    def __repr__(self):
        return "<%s(title='%s')>" % (self.__class__.name, self.title)


BlogModelBase.metadata.create_all(engine)
BlogModelSession = sessionmaker(bind=engine)
