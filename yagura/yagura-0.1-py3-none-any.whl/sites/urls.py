from django.urls import path
from yagura.sites import views


app_name = 'sites'
urlpatterns = [
    path('', views.SiteListView.as_view(), name='list'),
    path('<uuid:pk>', views.SiteDetailView.as_view(), name='detail'),
    path('new', views.SiteCreateView.as_view(), name='create'),
]
