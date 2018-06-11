from django.conf.urls import url
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from jwt_views import session_jwt_token
from . import views

urlpatterns = [
    url(r'^authorize/$', views.authorize, name='auth-authorize'),
    url(r'^code_callback/$', views.authorize_callback, name='auth-callback'),
    url(r'^home/$', views.home, name='auth-home'),
    url(r'^unconfigured/$', TemplateView.as_view(template_name='gcb_web_auth/unconfigured.html'), name='auth-unconfigured'),
    # JSON Web Token endpoints
    url(r'^api-token-auth/', obtain_jwt_token, name='auth-api-token-auth'),
    url(r'^api-token-refresh/', refresh_jwt_token, name='auth-api-token-refresh'),
    url(r'^api-token-verify/', verify_jwt_token, name='auth-api-token-verify'),
    url(r'^api-token-session/', session_jwt_token, name='auth-api-token-session'),
]
