from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AccountConfig(AppConfig):
    name = 'quickstartup.qs_accounts'
    verbose_name = _("Accounts")
