from django.urls import path, reverse_lazy
from django.views.generic import RedirectView
from yagura.core.views import IndexView


urlpatterns = [
    path('', IndexView.as_view()),
    path(
        'dashboard',
        RedirectView.as_view(url=reverse_lazy('sites:list')),
        name='dashboard'),
]
