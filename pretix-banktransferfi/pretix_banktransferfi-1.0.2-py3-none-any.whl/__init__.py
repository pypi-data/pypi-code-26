from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

from pretix import __version__ as version


class BankTransferFiApp(AppConfig):
    name = 'pretix_banktransferfi'
    verbose_name = _("Bank transfer FI")

    class PretixPluginMeta:
        name = _("Bank transfer FI")
        author = _("Felipe Morato")
        version = version
        description = _("Bank transfer payment option that creates a reference number (viitenumero) compliant with Finnish banks")
        visible = True
        version = '1.0.2'

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretix_banktransferfi.BankTransferFiApp'
