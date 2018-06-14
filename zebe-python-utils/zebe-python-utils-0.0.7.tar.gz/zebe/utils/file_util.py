# -*- coding: utf-8 -*-
"""
    zebe.util.file_util
    ~~~~~~~~~~~~~~~~

    文件工具类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

import os

import shutil


def copy_folder(source, target, override=True):
    """
    拷贝文件夹
    :param source: 原始文件夹
    :param target: 目标文件夹
    :param override: 是否覆盖，默认为是
    :return:
    """
    if os.path.exists(target):
        if override:
            shutil.rmtree(target)
        else:
            print("拷贝文件夹失败，目标文件夹已存在")
            return False
    shutil.copytree(source, target)
