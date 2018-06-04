from django.conf.urls import url
from PMIofKCM import views
urlpatterns = [
	url(r'^$', views.pmi),
]
