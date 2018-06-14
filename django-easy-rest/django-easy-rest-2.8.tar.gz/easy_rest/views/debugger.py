import sys
import json
import traceback
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from ..utils.utils import reverse_lazy
from uuid import uuid4
from rest_framework.response import Response
from django.http.response import HttpResponseForbidden
from django.conf import settings


class DebugHandler(object):
    def __init__(self, request, data, status):
        self.request = request
        self.data = data
        self.status = status

    def handle(self):
        token = str(uuid4())
        self.request.session['debug_info_api'] = {
            "token": token,
            "data": self.data
        }
        # force save
        self.request.session.save()
        self.data['debug_url'] = reverse_lazy("easy_rest:debugger") + "?token={}".format(token)
        return Response(data=self.data, status=self.status)


class DebugObject(object):
    def __init__(self, tb, handler):
        self.tb = tb
        self.handler = handler
        exc_type, exc_value, exc_traceback = sys.exc_info()
        self.trace = traceback.format_exception(exc_type, exc_value, exc_traceback)

    def serialize(self):
        return {
            "error": repr(self.tb),
            "trace": self.get_trace(),
            "handler": self.handler,
        }

    def get_trace(self):
        return [t.lstrip().rstrip().replace("\n", "").replace("\r", "") for t in self.trace]


class DebugCache(object):
    def __init__(self):
        self.cache = []

    def update(self, tb, handler):
        self.cache.append(DebugObject(tb, handler).serialize())

    def serialize(self):
        data = []
        for obj in self.cache:
            data.append(obj)
        return data


class TbFile(object):
    data = ""

    def write(self, data):
        self.data += data

    def read(self):
        return self.data


def get_error(error):
    if hasattr(error, '__traceback__') and hasattr(error, 'tb_frame'):
        trace = ''.join(traceback.format_tb(error.__traceback__))
    else:
        trace = 'Unknown traceback object type({}) has no attribute __traceback__'.format(type(error))

    return trace


def create_trace(last_error):
    error = last_error['error']
    handler = last_error['handler']
    del last_error['error']
    del last_error['handler']

    return {
        "type": get_error(error),
        "details": traceback.format_exception(**last_error),
        "handler": handler
    }


class DebugView(TemplateView):
    template_name = "easy_rest/debug.html"

    def get(self, request, *args, **kwargs):
        debug_data = self.request.session.get("debug_info_api")
        if not debug_data:
            return HttpResponseForbidden()
        token = request.GET.get("token")

        if token != debug_data['token']:
            if settings.DEBUG:
                print("real token is ", debug_data['token'], "got", token)
            return HttpResponseForbidden("Invalid token")

        response = super(DebugView, self).get(request, *args, **kwargs)

        return response

    def get_context_data(self, **kwargs):
        debug_data = self.request.session.get("debug_info_api")['data']
        ctx = super(DebugView, self).get_context_data(**kwargs)
        if "input" in debug_data:
            request = debug_data["input"]
            request_data = request['request_data']
            ctx["api_input"] = json.dumps(request_data, indent=1)
            ctx["api_code"] = request["request_code"]
        if 'debug_url' in debug_data:
            del debug_data['debug_url']
        if "input" in debug_data:
            del debug_data['input']
        ctx['output'] = json.dumps(debug_data, indent=1)
        tb = self.request.session.get("last_debug_error")
        if tb:
            ctx['traceback'] = json.dumps(tb, indent=1)

        return ctx
