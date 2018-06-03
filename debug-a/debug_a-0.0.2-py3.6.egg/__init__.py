# -*- coding: utf-8 -*-
import os

# 元信息
__version__ = '0.0.2'
__author__ = "zengbin93"
__email__ = "zeng_bin8888@163.com"


# 准备好文件夹
USER_HOME = os.path.expanduser('~')
PATH = os.path.join(USER_HOME, ".debug_a")
LOG_DIR = os.path.join(USER_HOME, ".debug_a/log/")
DATA_DIR = os.path.join(USER_HOME, ".debug_a/data/")
ACCOUNT_DIR = os.path.join(USER_HOME, ".debug_a/account/")
POOL_DIR = os.path.join(USER_HOME, ".debug_a/pool/")
for P in [PATH, LOG_DIR, DATA_DIR, ACCOUNT_DIR, POOL_DIR]:
    if not os.path.exists(P):
        os.mkdir(P)


from debug_a.utils import print_constitutions

