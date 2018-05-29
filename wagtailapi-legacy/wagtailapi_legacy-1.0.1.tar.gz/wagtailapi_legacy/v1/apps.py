from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig, apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class WagtailAPIAppConfig(AppConfig):
    name = 'wagtailapi_legacy.v1'
    label = 'wagtailapi_legacy_v1'
    verbose_name = "Wagtail API"

    def ready(self):
        # Install cache purging signal handlers
        if getattr(settings, 'WAGTAILAPI_USE_FRONTENDCACHE', False):
            if apps.is_installed('wagtail.contrib.wagtailfrontendcache'):
                from wagtailapi_legacy.v1.signal_handlers import register_signal_handlers
                register_signal_handlers()
            else:
                raise ImproperlyConfigured(
                    "The setting 'WAGTAILAPI_USE_FRONTENDCACHE' is True but "
                    "'wagtail.contrib.wagtailfrontendcache' is not in INSTALLED_APPS."
                )

        if not apps.is_installed('rest_framework'):
            raise ImproperlyConfigured(
                "The 'wagtailapi' module requires Django REST framework. "
                "Please add 'rest_framework' to INSTALLED_APPS."
            )
