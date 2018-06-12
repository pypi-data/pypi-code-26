# -*- coding:utf-8 -*- 
__author__ = 'jiangjun'
__date__ = '2018/3/28 14:19 '

import json

import logging

# from utils.common_enum import ReturnEnum
# from utils.response import ResponseData

from .date_encoder import DateEncoder

# Get an instance of a logger
logger = logging.getLogger('django')


class JsonUtils:

    def obj_2_json_str(obj):
        """
        对象转换为json字符串
        :return:
        """
        if not obj:
            return ''
        dic_data = {}
        try:
            dic_data.update(obj.__dict__)
            dic_data.pop('_state', None)
            json_str = json.dumps(dic_data, ensure_ascii=False, cls=DateEncoder)
            return json_str
        except Exception as e:
            print("error", e)
            raise e


# from datetime import datetime
# from datetime import date
#
# d = {'now': datetime.now(), 'today': date.today(), 'i': 100, 'str': '哈哈乐视'}
# ds = json.dumps(d, cls=DateEncoder, ensure_ascii=False)
# print("ds type:", type(ds), "ds:", ds)
# l = json.loads(ds)
# print("l  type:", type(l), "ds:", l)

#{'_state': <django.db.models.base.ModelState object at 0x1115c54a8>, 'id': 37, 'create_time': datetime.datetime(2018, 4, 26, 17, 14, 18, 396593), 'update_time': datetime.datetime(2018, 4, 26, 17, 14, 18, 396623), 'project_name': '昆明市五华区麻园城中村电网改造二期项目', 'project_code': 'GDHY-2018-S-001-00010', 'project_area_id': 1, 'project_type_id': 1, 'project_level_id': 1, 'bidding_type_id': 1, 'batch': '0001', 'owner': '昆明供电局', 'invitation_address': '昆明', 'invitation_time': datetime.datetime(2018, 4, 9, 0, 0), 'build_year': '2018'}
