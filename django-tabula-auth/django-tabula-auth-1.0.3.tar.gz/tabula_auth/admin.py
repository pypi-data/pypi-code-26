from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, UserCreationForm
from .models import *
from django import forms


class TabulaUserCreationForm(UserCreationForm):
    class Meta:
        model = PhoneNumberUser
        fields = ("username", 'phone_number')


@admin.register(PhoneNumberUser)
class TabulaUserAdmin(UserAdmin):
    add_form = TabulaUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'phone_number'),
        }),
    )
