# -*- coding: utf-8 -*-
"""
    zebe.service.english
    ~~~~~~~~~~~~~~~~

    英语相关的服务

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

from zebe.modle.entity.english import EnglishPhrase, EnglishModelSession
from zebe.service.base import ModelBaseService


# 英语短语服务
class EnglishPhraseService(ModelBaseService):
    def __init__(self):
        super().__init__(EnglishPhrase, EnglishModelSession)

    # 通过首字母查找短语
    def find_all_by_first_letter(self, first_letter):
        result = None
        if first_letter is not None:
            result = self.session.query(self.entity).filter(self.entity.first_letter == first_letter).all()
            self.session.close()
        return result
