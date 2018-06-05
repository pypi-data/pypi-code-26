# -*- coding: utf-8 -*-
"""
    zebe.service.cdrvba
    ~~~~~~~~~~~~~~~~

    CorelDrawVBA相关的服务

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""
from sqlalchemy import func

from zebe.modle.entity.cdrvba import CorelDrawVBAArticle, CorelDrawVBAModelSession

from zebe.service.base import ModelBaseService


# CorelDrawVBA文章服务
class CorelDrawVBAArticleService(ModelBaseService):
    def __init__(self):
        super().__init__(CorelDrawVBAArticle, CorelDrawVBAModelSession)

    # 查询全部数据并按照日期倒序排列
    def find_all_ordered_by_time(self):
        result = self.session.query(self.entity).order_by(self.entity.create_time.desc()).all()
        self.session.close()
        return result

    # 根据标签随机查询指定数量的文章
    def find_random_articles_by_tag(self, amount, tag):
        total = self.count_all()
        max_query = amount if amount <= total else total
        result_title_set = set()
        result_article_list = []
        while True:
            if len(result_article_list) == max_query:
                self.session.close()
                print('------------------ 已成功根据标签[' + tag + ']找到' + str(max_query) + '篇随机文章。')
                break
            else:
                result = self.session.query(self.entity).filter(self.entity.title.like(tag + "%")).order_by(
                    func.random()).limit(1).one_or_none()
                if not (result.title in result_title_set):
                    result_article_list.append(result)
                    result_title_set.add(result.title)
                    print('根据标签[' + tag + ']找到一篇随机文章：' + result.title)
                else:
                    print('根据标签[' + tag + ']找到一篇随机文章：' + result.title + '，但文章重复，重新查找')
        return result_article_list
