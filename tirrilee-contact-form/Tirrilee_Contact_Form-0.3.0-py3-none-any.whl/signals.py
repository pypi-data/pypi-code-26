from __future__ import unicode_literals
from django.dispatch import Signal

before_send = Signal(providing_args=["request", "form"])
after_send = Signal(providing_args=["message", "form"])