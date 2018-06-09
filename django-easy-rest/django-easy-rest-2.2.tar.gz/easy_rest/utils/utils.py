from django.conf import settings
from django.urls import reverse_lazy as r_l
import os

root = '/easy_rest'
# if easy rest root specified in settings
if hasattr(settings, 'EASY_REST_ROOT_URL'):
    root = "/" + settings.EASY_REST_ROOT_URL


def reverse_lazy(pattern):
    app, name = pattern.split(":")
    if app == "easy_rest":
        return os.path.join(root, name)
    return r_l(pattern)
