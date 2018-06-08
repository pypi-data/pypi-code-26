# -*- coding: utf-8 -*-

"""
gwc.login
该模块包含日志记录、字符串加密和解密函数
"""

from __future__ import print_function

import logging
import os

LOG_FILENAME = os.path.join(os.getcwd(), 'gwc.log')
LOG_FORMAT = "[%(asctime)s] - %(filename)s - %(funcName)s - %(lineno)d - [%(levelname)s] : %(message)s"


def init_logger():
    """
    初始化记录日志信息
    """
    logging.captureWarnings(True)
    logging.basicConfig(filename=LOG_FILENAME, format=LOG_FORMAT)
    logger = logging.getLogger("GeneDock")
    logger.setLevel(logging.INFO)

    return logger


def encrypt(text, num=19):
    """
    加密函数
    """
    ori_array = bytearray(str(text).encode("utf-8"))
    count = len(ori_array)
    new_array = bytearray(count * 2)
    j = 0
    for i in range(0, count):
        ori_ele = ori_array[i]
        xor_ori_ele = ori_ele ^ num
        new_ele1 = xor_ori_ele % 16
        new_ele2 = xor_ori_ele // 16
        new_ele1 = new_ele1 + 48
        new_ele2 = new_ele2 + 99
        new_array[j] = new_ele1
        new_array[j + 1] = new_ele2
        j = j + 2
    return new_array.decode("utf-8")


def decrypt(text, num=19):
    """
    解密函数
    """
    new_array = bytearray(str(text).encode("utf-8"))
    count = len(new_array)
    if count % 2 != 0:
        return ''
    count = count // 2
    ori_array = bytearray(count)
    j = 0
    for i in range(0, count):
        new_ele1 = new_array[j]
        new_ele2 = new_array[j + 1]
        j = j + 2
        new_ele1 = new_ele1 - 48
        new_ele2 = new_ele2 - 99
        xor_ori_ele = new_ele2 * 16 + new_ele1
        ori_ele = xor_ori_ele ^ num
        ori_array[i] = ori_ele
    return ori_array.decode("utf-8")
