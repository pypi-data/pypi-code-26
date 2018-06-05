# -*- coding: utf-8 -*-
"""
    zebe.service.memory
    ~~~~~~~~~~~~~~~~

    记忆相关的服务

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from zebe.modle.entity.memory import NumberCode, MemoryModelModelSession
from zebe.service.base import ModelBaseService


class NumberCodeService(ModelBaseService):

    def __init__(self):
        super().__init__(NumberCode, MemoryModelModelSession)

    def find_one_by_number(self, number):
        """
        通过数字查找一条记录
        :param number: 数字
        :return:
        """
        result = self.session.query(self.entity).filter(self.entity.number == number).one_or_none()
        self.session.close()
        return result

    def get_all_number_code_dict(self):
        """
        获取所有数字和编码的对应字典
        :return:
        """
        result = {}
        numbers = self.find_all()
        for data in numbers:
            result[data.number] = data.code
        return result
