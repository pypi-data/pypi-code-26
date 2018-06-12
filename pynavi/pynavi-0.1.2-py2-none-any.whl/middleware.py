# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)
import json
import logging
import time
import traceback
import uuid

from django.utils.deprecation import MiddlewareMixin

from pynavi.clients.sentry import report_capture
from pynavi.exceptions import NaviException
from pynavi.view.reqponse import NaviJsonResponse, SYSTEM_ERROR

BUILD_IN_MIDDLEWARE = [
    'pynavi.middleware.NaviMetaInfoMiddleware',
    'pynavi.middleware.NaviExceptionMiddleware',
]


class NaviRequestTraceMiddleware(MiddlewareMixin):
    """NAVI 元数据信息处理过滤器"""

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('django.api')
        self.logger.setLevel(logging.INFO)
        super(NaviRequestTraceMiddleware, self).__init__(*args, **kwargs)

    def process_request(self, request):
        request.META['XFLAG'] = str(uuid.uuid1()).replace('-', '')

        self.logger.info('[REQUEST] XFLAG: {}, HEADERS: {}, SESSION: {}, URL: {}, GET: {}, POST: {}'.format(
            request.META['XFLAG'], str(request.META), str(request.session._session), request.path, str(request.GET.dict()), str(request.POST.dict())
        ))

    def process_response(self, request, response):
        self.logger.info('[RESPONSE] XFLAG: {} , RES: {}'.format(
            request.META['XFLAG'], str(response.content)
        ))

        return response


class NaviMetaInfoMiddleware(MiddlewareMixin):
    """NAVI 元数据信息处理过滤器"""

    _REQUEST_START_TIME = '_REQUEST_START_TIME'

    def process_request(self, request):
        request.META[self._REQUEST_START_TIME] = time.time()  # 秒为单位

    def process_response(self, request, response):
        try:
            start_time = request.META[self._REQUEST_START_TIME]
            now = time.time()

            cost = (now - start_time)

            if response.content:
                ret = json.loads(response.content)
                ret.update({'cost': cost})
                response.content = json.dumps(ret)
        except Exception as e:
            print(e.message)

        return response


class NaviExceptionMiddleware(MiddlewareMixin):
    """pynavi 异常处理类"""

    def process_exception(self, request, exception):
        if isinstance(exception, NaviException):
            return NaviJsonResponse(code=exception.code, message=exception.message)

        traceback.print_exc()

        return NaviJsonResponse(code=SYSTEM_ERROR.code, message=SYSTEM_ERROR.message_en)


class NaviSentryReportMiddleware(MiddlewareMixin):
    """sentry 异常上报"""

    def process_exception(self, request, e):
        if not isinstance(e, NaviException):
            report_capture()
