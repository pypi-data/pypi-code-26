from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import GoodreadsProvider

urlpatterns = default_urlpatterns(GoodreadsProvider)
