from django.urls import reverse_lazy
from django.views.generic import TemplateView
from ..utils.utils import reverse_lazy
from uuid import uuid4
from rest_framework.response import Response
from django.http.response import HttpResponseForbidden
import json
from django.conf import settings
import traceback
import sys


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
        if 'debug_url' in debug_data:
            del debug_data['debug_url']
        ctx['output'] = json.dumps(debug_data, indent=1)
        ctx['traceback'] = self.request.session.get('last_debug_error', None)
        return ctx
