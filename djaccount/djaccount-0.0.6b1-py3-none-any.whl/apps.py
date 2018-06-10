from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AccountConfig(AppConfig):
    name = 'account'
    verbose_name = _('Account')

    def ready(self):
        from django.urls import register_converter
        from .converters import AccountConverter
        register_converter(AccountConverter, 'account')
