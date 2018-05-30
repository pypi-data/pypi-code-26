from django.urls import path
from authorized import views
urlpatterns = [
    path('test/', views.sample),
]