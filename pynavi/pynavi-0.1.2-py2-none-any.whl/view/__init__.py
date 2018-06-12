# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)

from functools import wraps

from django.utils.decorators import available_attrs

from pynavi.exceptions import APIException
from pynavi.view.reqponse import NaviJsonResponse, AUTH_ERROR


def login_required(func):
    """用户登录验证"""

    @wraps(func, assigned=available_attrs(func))
    def wrapper(request, *args, **kws):
        if not request.user.is_anonymous():
            return func(request, *args, **kws)

        raise APIException(error_code=AUTH_ERROR)

    return wrapper
