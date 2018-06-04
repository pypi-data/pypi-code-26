"""URL Configuration."""
from django.conf import settings
from django.urls import include, path
from django.http import HttpResponse


def build_urlpatterns(*paths):
    """
    Generate urlpatterns, adding URL_PREFIX and health checks.

    Valid input is what would normally be assigned in urlpatterns

    ```
    paths = [
        path('', include('{project}.apps.{app}.urls'))
    ]
    ```
    """
    # Paths that check services health
    system_check_paths = [
        path('healthz', lambda request: HttpResponse(status=200), name='health-check'),
        path('readyz', lambda request: HttpResponse(status=200), name='ready-check'),
    ]

    return [
        path(settings.URL_PREFIX, include(list(paths) + system_check_paths)),
    ]
