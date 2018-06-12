# -*- coding: utf-8 -*-

import traceback

from django.conf import settings
from raven.contrib.django.raven_compat.models import client, ProxyClient


class DummySentryClient(ProxyClient):

    def captureException(self):
        traceback.print_exc()


navi_sentry_client = DummySentryClient() if settings.DEBUG else client


def report_capture():
    navi_sentry_client.captureException()
