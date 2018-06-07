# -*- coding: utf-8 -*-
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import (
	test,
)


class testCreateView(CreateView):

    model = test


class testDeleteView(DeleteView):

    model = test


class testDetailView(DetailView):

    model = test


class testUpdateView(UpdateView):

    model = test


class testListView(ListView):

    model = test

