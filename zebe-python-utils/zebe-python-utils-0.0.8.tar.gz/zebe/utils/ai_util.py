# -*- coding: utf-8 -*-
"""
    zebe.util.ai_util
    ~~~~~~~~~~~~~~~~

    人工智能工具类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

import json
import requests


def get_tuling_robot_reply(question):
    """
    获取图灵机器人回复
    :param question: 问题
    :return: 返回回答
    """
    url = 'http://www.tuling123.com/openapi/api'
    data = {u"key": "f62c4ad38b9a441cb5596d73f5d65af0", "info": question, "userid": "1234"}
    response = requests.post(url, data).content
    return json.loads(response, encoding='utf-8')["text"]