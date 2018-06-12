# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)
import datetime
import functools
import inspect
import json
import os
import sys

from django.conf.urls import url as django_url, include
from django.views.generic.base import View

from pynavi.exceptions import APIException
from pynavi.view.request import PType


def param(**p_kwargs):
    """
    Usage:
    @param(param1=PType.str)
    @param(param1={'type':PType.int, 'default':0, 'null'=False})
    @param(param1=(PType.str, 0, False))
    """

    def param_decorator(func):
        @functools.wraps(func)
        def wrapper(view, *args, **kwargs):
            request = args[0]
            # params = deepcopy(request.GET)
            # params.update(request.POST)

            m = {'get': request.GET, 'post': request.POST}
            method = m[func.__name__]

            for k, rules in p_kwargs.items():
                _name = str(k)  # 参数名
                _type = PType.str  # 参数类型
                _default = None  # 默认值
                _null = True  # 可否为空
                _format = ''  # 格式化

                if type(rules) == int:  # PType
                    _type = rules
                elif type(rules) == dict:
                    _type = rules['type'] if 'type' in rules else _type
                    _default = rules['default'] if 'default' in rules else _default
                    _null = rules['null'] if 'null' in rules else _null
                    _format = rules['format'] if 'format' in rules else _format
                elif type(rules) == tuple and len(rules) > 0:
                    _type = rules[0]
                    _default = rules[1] if len(rules) >= 2 else _default
                    _null = rules[2] if len(rules) >= 3 else _null

                # 文件类型参数特殊处理
                try:
                    if _type == PType.file:
                        if func.__name__ != 'post':
                            raise APIException(-1, '文件类型参数必须使用POST方式调用')

                        v = request.FILES.get(_name, None)
                    else:
                        v = ','.join(method.getlist(_name, None)).strip() if _name in method else None
                except KeyError:
                    v = None

                # 默认值处理
                if v is None and _default is not None:
                    v = _default

                # 参数非空校验
                if not _null and v is None:
                    raise APIException(-1, '参数{}不可为空'.format(_name))

                if v:
                    if _type == PType.str_list:
                        v = [item for item in v.split(',') if len(item) > 0]
                    elif _type == PType.int_list:
                        v = [int(item) for item in v.split(',')]
                    elif _type == PType.float_list:
                        v = [float(item) for item in v.split(',')]
                    elif _type == PType.json:
                        try:
                            v = json.loads(v)
                        except ValueError:
                            raise APIException(-1, '参数错误')
                    elif _type == PType.str:
                        v = str(v)
                    elif _type == PType.int:
                        v = int(v)
                    elif _type == PType.float:
                        v = float(v)
                    elif _type == PType.datetime:
                        v = datetime.datetime.strptime(str(v), _format if _format else '%Y-%m-%d %H:%M:%S')

                kwargs.update({k: v})

            return func(request, *args, **kwargs)

        return wrapper

    return param_decorator


def url(regex, *args, **kwargs):
    """系统启动时自动注册url访问pattern，urls文件的另一种实现方式"""

    def func_wrapper(cls):

        @functools.wraps(cls)
        def wrapper(request, *args, **kwargs):
            if not issubclass(cls, View):
                raise APIException(-1, '系统错误')

            return cls

        module = sys.modules[cls.__module__]
        if not hasattr(module, 'urlpatterns'):
            module.urlpatterns = []

        module.urlpatterns.append(
            django_url(
                regex, cls.as_view(), *args, **kwargs
            ),
        )
        return wrapper

    return func_wrapper


def url_patterns_maker(module, **kwargs):
    path_init = inspect.getouterframes(inspect.currentframe())[1][1]
    path_views, init_file = os.path.split(path_init)

    view_files = [
        f.split('.')[0] for f in os.listdir(path_views) if not f.startswith('_') and (f.endswith('.py') or os.path.isdir(os.path.join(path_views, f))) and init_file != f
    ]

    urlpatterns = []
    default_prefix = kwargs['default'] if 'default' in kwargs else ''
    for view_file in view_files:
        if view_file in kwargs:
            urlpatterns.append(
                django_url(r'{0}{1}'.format(default_prefix, kwargs[view_file]), include('{0}.{1}'.format(module, view_file)))
            )
        else:
            urlpatterns.append(
                django_url(r'^{0}'.format(default_prefix), include('{0}.{1}'.format(module, view_file)))
            )

    return urlpatterns
