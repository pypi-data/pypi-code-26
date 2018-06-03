from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView
from yagura.sites import models, forms


class SiteDetailView(LoginRequiredMixin, DetailView):
    """Site detail view

    TODO: Custom 404 from request not-found pk
    """
    model = models.Site


class SiteListView(LoginRequiredMixin, ListView):
    model = models.Site


class SiteCreateView(LoginRequiredMixin, CreateView):
    model = models.Site
    form_class = forms.SiteCreateForm

    def form_valid(self, form: forms.SiteCreateForm):
        form.instance.created_by = self.request.user
        form.instance.save()
        return super().form_valid(form)
