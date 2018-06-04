# -*- coding: utf-8 -*-

from django.http import Http404
from django.http import HttpResponsePermanentRedirect
from django.views.generic import View

from django_store.store import MinioStore


class MinioDownloadView(View):

    def get(self, request, *args, **kwargs):
        query = request.GET.copy()
        file_name = query.get('file', None)

        if file_name is None:
            raise Http404()

        mc = MinioStore()
        return mc.download(file_name)


class MinioOpenView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.copy()
        file_name = query.get('file', None)

        if file_name is None:
            raise Http404()

        mc = MinioStore()
        return mc.open(file_name)


class MinioSignedView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.copy()
        file_name = query.get('file', None)

        if file_name is None:
            raise Http404()

        mc = MinioStore()
        url = mc.get_presigned_object(file_name)
        return HttpResponsePermanentRedirect(url)
