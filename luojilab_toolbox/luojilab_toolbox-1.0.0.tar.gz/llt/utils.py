# -*- coding: utf-8 -*-
import types
import string
import random
import datetime


def unicode_truncate(uni, length, encoding='utf-8', triple_dot=True):
    """
    按字节长度对字符串进行截取
    :param uni: 待截取字符串，unicode编码格式
    :param length: 截取后字符串长度
    :param encoding: 转换时采用的编码格式
    :param triple_dot: 截取后末尾是否包含"..."
    :return: 截取后的字符串，unicode编码格式
    """
    encoded = uni.encode(encoding)
    if len(encoded) <= length:
        return uni

    dot = '...' if triple_dot else ''
    return u'%s%s' % (encoded[:length - len(dot)].decode(encoding, 'ignore'), dot)


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    对指定字符串进行编码转换
    :param s: 待转换的字符串对象
    :param encoding: 编码格式
    :param strings_only: 是否仅转换字符串对象
    :param errors:
    :return: 编码转换后的字符串
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                                           errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s


def random_str(length=8):
    """
    获取指定长度随机字符串（字母+数字）
    :param length: 随机字符串长度
    :return: 随机字符串
    """
    chars = string.ascii_lowercase + string.digits
    return ''.join([random.choice(chars) for _ in range(length)])


def random_id():
    """
    获取随机数字（不保证不重复）
    :return: 随机数字
    """
    now = datetime.datetime.now()
    return int(now.strftime('%Y%m%d%H%M%S')) * (10 ** 8) + random.randint(1, 99999999)


def sequence_generator(random_length=2):
    """
    序列号生成器（理论上单机不重复）
    :return: 序列号
    """
    now = datetime.datetime.now()
    sequence = int(now.strftime('%Y%m%d%H%M%S%f'))

    if random_length > 0:
        sequence = sequence * (10 ** random_length) + random.randint(1, 10 ** random_length - 1)

    return sequence


def get_key_by_value(dic, value):
    dict_reverse = {value: key for key, value in dic}
    return dict_reverse.get(value)
