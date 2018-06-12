# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from pynavi.exceptions import APIException
from pynavi.view import login_required, AUTH_ERROR


class NaviAPIView(View):

    def _validate(self, request, *args, **kwargs):
        """继承自NaviAPIView的类，在这里进行基本参数格式校验"""
        pass

    @classmethod
    def as_view(cls, **kwargs):
        view = super(NaviAPIView, cls).as_view(**kwargs)
        return csrf_exempt(view)


class AuthAPIView(NaviAPIView):

    @classmethod
    def as_view(cls, **kwargs):
        view = super(AuthAPIView, cls).as_view(**kwargs)
        return login_required(view)


class InternalAPIView(NaviAPIView):
    """内部交互接口"""

    def __init__(self, api_keys, **kwargs):
        super(InternalAPIView, self).__init__(**kwargs)
        self._SUPPORTED_API_KEYS = api_keys if api_keys else []

    def _validate(self, request, *args, **kwargs):
        # 校验API_KEY是否合法
        api_key = request.META.get('HTTP_APIKEY')
        if not api_key or api_key not in self._SUPPORTED_API_KEYS:
            raise APIException(error_code=AUTH_ERROR, message='api key invalid')
