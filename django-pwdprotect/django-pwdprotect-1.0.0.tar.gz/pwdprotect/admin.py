from __future__ import absolute_import, unicode_literals

from django.contrib import admin

from .models import PasswordProtectedUrl


@admin.register(PasswordProtectedUrl)
class PasswordProtectedUrlAdmin(admin.ModelAdmin):
    list_display = ["url", "username", "password"]
