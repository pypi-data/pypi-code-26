# -*- coding: utf-8 -*-
"""
    zebe.service.diary
    ~~~~~~~~~~~~~~~~

    日记相关的服务

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""
from datetime import datetime

from zebe.modle.entity.diary import Diary, DiaryModelSession
from zebe.service.base import ModelBaseService


# 日记服务
class DiaryService(ModelBaseService):
    def __init__(self):
        super().__init__(Diary, DiaryModelSession)

    def find_one_by_title(self, title):
        """
        通过标题查找一篇日记
        :param title: 标题
        :return:
        """
        result = None
        if title is not None:
            result = self.session.query(self.entity).filter(self.entity.title == title).one_or_none()
            self.session.close()
        return result

    def find_all_by_date(self, year, month, day):
        """
        按日期查询全部数据
        :param year: 年
        :param month: 月
        :param day: 日
        :return:
        """
        result = self.session.query(self.entity).filter(self.entity.year == year, self.entity.month == month,
                                                        self.entity.day == day).all()
        self.session.close()
        return result

    def find_all_by_year(self, year):
        """
        按年查询全部数据
        :param year: 年
        :return:
        """
        result = self.session.query(self.entity).filter(self.entity.year == year).all()
        self.session.close()
        return result

    def find_all_by_month(self, year, month):
        """
        按月查询全部数据
        :param year: 年
        :param month: 月
        :return:
        """
        result = self.session.query(self.entity).filter(self.entity.year == year, self.entity.month == month).all()
        self.session.close()
        return result

    def find_all_by_today(self):
        """
        查询今天全部数据
        :return:
        """
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        return self.find_all_by_date(year, month, day)

    def find_all_by_this_month(self):
        """
        查询本月的全部数据
        :return:
        """
        now = datetime.now()
        year = now.year
        month = now.month
        return self.find_all_by_month(year, month)

    def find_all_by_this_year(self):
        """
        查询本年的全部数据
        :return:
        """
        now = datetime.now()
        year = now.year
        return self.find_all_by_year(year)

    def find_all_order_by_date(self):
        """
        查询全部数据并指定排序
        :return:
        """
        result = self.session.query(self.entity).order_by(self.entity.create_time.desc()).all()
        self.session.close()
        return result

    @staticmethod
    def get_total_learn_count(diary_list):
        """
        计算一组日记列表的总收获数量
        :param diary_list: 日记列表
        :return:
        """
        total = 0
        if diary_list is not None:
            for diary in diary_list:
                total += diary.learned
        return total
