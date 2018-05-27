# encoding=utf8
from __future__ import unicode_literals

import sys
import logging

import pyotp

from mohand.hands import hand

if sys.version > '3':
    PY3 = True
else:
    PY3 = False

LOG_FORMAT = "[%(asctime)s][%(name)s:%(lineno)s][%(levelname)s] %(message)s"
logging.basicConfig(
    level=logging.WARN,
    format=LOG_FORMAT,
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def otp(*dargs, **dkwargs):
    """
    将被装饰函数封装为一个 :class:`click.core.Command` 类，成为 ``mohand`` 的子命令

    该装饰器被作为一个包含定制其行为的含参数装饰器使用（如： ``@hand.otp(secret='xxoo')`` ）

    .. note::

        该装饰器最终会通过插件系统被注册到 :data:`.hands.hand` 中。

        此处的 ``otp`` 装饰器本身是应该不支持无参数装饰的，但考虑到其作为样例实现，
        故将其实现为兼容两种传参的装饰器

    :param int log_level: 当前子命令的日志输出等级，默认为： ``logging.INFO``
    :param str secret: 用于构造基于时间的 OTP 的秘钥字串
    :return: 被封装后的函数
    :rtype: function
    """
    invoked = bool(len(dargs) == 1 and not dkwargs and callable(dargs[0]))
    if invoked:
        func = dargs[0]

    def wrapper(func):
        @hand._click.command(
            name=func.__name__.lower(),
            help=func.__doc__)
        def _wrapper(*args, **kwargs):
            log_level = dkwargs.pop('log_level', logging.INFO)
            log.setLevel(log_level)

            log.debug("decrator param: {} {}".format(dargs, dkwargs))
            log.debug("function param: {} {}".format(args, kwargs))

            with OTP(*dargs, **dkwargs) as o:
                func(o, *args, **kwargs)
        return _wrapper
    return wrapper if not invoked else wrapper(func)


class OTP(object):
    """
    pyotp实例化后的对象封装，支持一系列接口方法
    """

    def __init__(self, secret=None):
        if not secret:
            raise ValueError('secret 值错误，不可为空')
        self.otp = pyotp.TOTP(secret)

    def __enter__(self):
        return self

    def now(self):
        """
        获取当前密码

        :return: OTP 密码
        :rtype: str
        """
        return self.otp.now()

    def format(self, fmt='{otp}', **kwargs):
        """
        格式化密码输出，用于应对 OTP 与指定字串进行拼接作为最终密码的场景。
        额外提供的格式化参数需要通过 ``**kwargs`` 传入

        :param str fmt: 格式化模板字串，将会调用其 str.format 方法
        :return: 格式化后的 OTP 密码
        :rtype: str
        :raises KeyError: fmt字串中指定的关键字参数未传入造成的格式化失败
        """
        dict_ = {'otp': self.now()}
        dict_.update(kwargs)
        return fmt.format(**dict_)

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type is None:
            return False
        elif exception_type is ValueError:
            # 返回 False 将异常抛出
            return False
        else:
            log.error('other error: {}\n{}'.format(exception_value, traceback))
            return False
