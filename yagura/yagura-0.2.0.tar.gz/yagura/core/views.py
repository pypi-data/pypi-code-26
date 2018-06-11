from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.urls import reverse_lazy


class IndexView(TemplateView):
    template_name = 'index.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_anonymous:
            return redirect(reverse_lazy('dashboard'))
        return super().dispatch(request, *args, **kwargs)
