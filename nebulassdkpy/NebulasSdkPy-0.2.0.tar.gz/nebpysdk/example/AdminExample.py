# -*- coding: utf-8 -*-
# @Time    : 2018/6/3 下午9:27
# @Author  : GuoXiaoMin
# @File    : AdminExample.py
# @Software: PyCharm
from sdk.src.client.Neb import Neb
import json

neb = Neb()

print(neb.admin.nodeInfo())

print(neb.admin.account())

print(neb.admin.getConfig())