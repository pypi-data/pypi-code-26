from django.urls import path
from . import views

urlpatterns = [

    path('open_url/', views.OpenURL.as_view(), name='radiant-open_url'),
    path('logs/', views.Logs.as_view(), name='radiant-logs'),
    path('mdc-theme.css/', views.Theme.as_view(), name='mdc-theme.css'),

]
