# -*- coding: utf-8 -*-
"""
    zebe.util.entity_util
    ~~~~~~~~~~~~~~~~

    实体工具类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

import json
from datetime import datetime as type_datetime


def wrap_entity_by_form_data(instance, request):
    """
    根据表单请求包装实体
    :param instance: 实体类的实例
    :param request:
    :return: 返回填充表单属性后的实例
    """
    public_fields = get_public_fields_of_entity(instance)
    for key, value in request.form.items():
        if key in public_fields:
            if hasattr(instance, key):
                setattr(instance, key, value)
    return instance


def get_public_fields_of_entity(instance):
    """
    获取实体类的公开属性
    :param instance: 实体类的实例
    :return: 返回公开属性列表
    """
    public_fields = []
    if hasattr(instance, '_sa_instance_state'):
        keys = instance._sa_instance_state.attrs._data.keys()
        for field in keys:
            public_fields.append(field)
    return public_fields


def entity_to_dict(instance):
    """
    实体类转换成字典
    :param instance: 实体类的实例
    :return: 返回实体类转换后的字典
    """
    fields = get_public_fields_of_entity(instance)
    result_dict = {}
    for field in fields:
        result_dict[field] = get_entity_value_or_empty(instance, field)
    return result_dict


def get_entity_value_or_empty(instance, field):
    """
    获取对象某个属性的值
    :param instance: 实体类的实例
    :param field: 属性名称
    :return: 返回具体属性的值，如果值是None则返回空串，如果是日期，则返回格式化后的字符串格式日期
    """
    if instance is not None and field is not None and hasattr(instance, field):
        value = getattr(instance, field)
        if value is not None:
            return value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, type_datetime) else value
    return ''


# 实体类数据转换为JSON
def dump_entity_data_to_json(instance):
    """
    实体类数据转换为JSON
    :param instance: 实体类的实例
    :return:
    """
    return json.dumps(instance, default=entity_to_dict, ensure_ascii=False)
