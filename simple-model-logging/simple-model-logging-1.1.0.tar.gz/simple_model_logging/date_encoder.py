__author__ = 'jiangjun'
__date__ = '2018/4/17 上午10:22'

import json
import datetime


class DateEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H-%M-%S")
        if isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, o)