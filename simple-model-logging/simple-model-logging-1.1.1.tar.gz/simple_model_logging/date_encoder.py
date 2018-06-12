__author__ = 'jiangjun'
__date__ = '2018/4/17 上午10:22'

import json
import datetime

from django.db import models


class DateEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H-%M-%S")
        if isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        if isinstance(o, models.ImageField):
            return o.name
        if isinstance(o, models.FileField):
            return o.name
        else:
            return json.JSONEncoder.default(self, o)