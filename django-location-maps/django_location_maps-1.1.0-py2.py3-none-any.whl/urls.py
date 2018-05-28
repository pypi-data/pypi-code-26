from django.conf.urls import url, include

from .api.urls import router

urlpatterns = [
    url(r'^', include(router.urls)),
]
