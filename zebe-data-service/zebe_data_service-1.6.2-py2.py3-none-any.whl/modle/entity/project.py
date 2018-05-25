# -*- coding: utf-8 -*-
"""
    zebe.model.entity.project
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    项目相关的实体类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from datetime import datetime

from sqlalchemy import Column, String, Integer, SmallInteger, Text, Float, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.config.db import PROJECT_DB

engine = create_engine('sqlite:///' + PROJECT_DB, echo=True)
ProjectModelBase = declarative_base()


# 项目
class Project(ProjectModelBase):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    name = Column(String(40), default="", nullable=False)  # 名称
    type = Column(String(10), default="", nullable=False, index=True)  # 类型
    is_main = Column(SmallInteger, default=0, nullable=False, index=True)  # 是否主要（0=否 1=是）
    description = Column(Text, default="", nullable=False)  # 描述
    year = Column(SmallInteger, default=0, nullable=False, index=True)  # 年份
    relative_url = Column(String(300), default="", nullable=False)  # 相关链接
    cover = Column(String(300), default="", nullable=False)  # 封面图
    total_task = Column(Integer, default=0, nullable=False)  # 总任务数
    finished_task = Column(Integer, default=0, nullable=False)  # 已完成任务数
    estimated_time = Column(Integer, default=-1, nullable=False)  # 预估时长（分）
    progress = Column(Float, default=0.0, nullable=False)  # 进度
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间
    finish_time = Column(DateTime)  # 完成时间

    def __repr__(self):
        return "<%s(name='%s')>" % (self.__class__.name, self.name)


# 任务
class Task(ProjectModelBase):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    title = Column(String(50), default="", nullable=False)  # 标题
    project_id = Column(Integer, default=0, nullable=False, index=True)  # 所属项目ID
    estimated_time = Column(Integer, default=-1, nullable=False)  # 预估时长（分）
    status = Column(SmallInteger, default=0, nullable=False, index=True)  # 状态（0=未完成 1=已完成）
    idx_order = Column(Integer, default=0, nullable=False)  # 排序
    is_assigned = Column(Integer, default=0, nullable=False)  # 是否已分配
    year = Column(SmallInteger, default=0, nullable=False, index=True)  # 年份
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间
    start_time = Column(DateTime)  # 开始时间
    end_time = Column(DateTime)  # 结束时间
    finish_time = Column(DateTime)  # 完成时间

    def __repr__(self):
        return "<%s(title='%s')>" % (self.__class__.name, self.title)


# 自动日常任务
class AutoDailyTask(ProjectModelBase):
    __tablename__ = 'auto_daily_task'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    title = Column(String(50), default="", nullable=False)  # 标题
    is_main = Column(SmallInteger, default=0, nullable=False, index=True)  # 是否主要（0=否 1=是）
    task_id = Column(Integer)  # 所属任务ID
    project_id = Column(Integer)  # 所属项目ID
    estimated_time = Column(Integer, default=-1, nullable=False)  # 预估时长（分）
    status = Column(SmallInteger, default=0, nullable=False, index=True)  # 状态（0=未完成 1=已完成）
    idx_order = Column(Integer, default=0, nullable=False)  # 排序
    year = Column(SmallInteger, default=0, nullable=False, index=True)  # 年份
    date = Column(String(10), default="", nullable=False, index=True)  # 日期
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间
    finish_time = Column(DateTime)  # 完成时间
    delay_count = Column(SmallInteger, default=0, nullable=False)  # 拖延次数

    def __repr__(self):
        return "<%s(title='%s')>" % (self.__class__.name, self.title)


ProjectModelBase.metadata.create_all(engine)
ProjectModelSession = sessionmaker(bind=engine)
