# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)


class NaviException(Exception):

    def __init__(self, code=0, message='', error_code=None):
        """
        构造navi 异常参数
        :param code:
        :param message:
        :param error_code: ErrorCode 类型
        """
        # 如果error_code不为空，则取error_code得错误码信息，优先级最高
        if error_code:
            self._code = error_code.code
            self._message = error_code.message_en
        else:
            self._code = code

        self._message = message

    @classmethod
    def custom_error(cls, message):
        from pynavi.view.reqponse import CUSTOMER_ERROR
        return cls(code=CUSTOMER_ERROR.code, message=message)

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message


class SystemException(NaviException):
    """系统异常"""

    def __init__(self, *args, **kwargs):
        super(SystemException, self).__init__(*args, **kwargs)


class BusinessException(NaviException):
    """业务逻辑异常"""

    def __init__(self, *args, **kwargs):
        super(BusinessException, self).__init__(*args, **kwargs)


class APIException(NaviException):
    """API接口逻辑异常"""

    def __init__(self, *args, **kwargs):
        super(APIException, self).__init__(*args, **kwargs)
