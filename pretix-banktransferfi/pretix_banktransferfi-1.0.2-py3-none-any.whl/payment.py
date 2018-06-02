import json
import textwrap
from collections import OrderedDict

from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from i18nfield.fields import I18nFormField, I18nTextarea
from i18nfield.strings import LazyI18nString

from pretix.base.models import Order
from pretix.base.payment import BasePaymentProvider

from pretix_banktransferfi.viitenumero import generate_viitenumero


class BankTransferFi(BasePaymentProvider):
    identifier = 'pretix-banktransferfi'
    verbose_name = _('Bank transfer FI')
    public_name = _('Bank transfer')

    @staticmethod
    def form_field_details(**kwargs):
        return I18nFormField(
            label=_('Bank account details'),
            widget=I18nTextarea,
            help_text=_('Include everything that your customers need to send you a bank transfer payment. Within SEPA '
                        'countries, IBAN, BIC and account owner should suffice. If you have lots of international '
                        'customers, they might also need your full address and your bank\'s full address.'),
            widget_kwargs={'attrs': {
                'rows': '4',
                'placeholder': _(
                    'e.g. IBAN: FI12 1234 5678 8765 4321\n'
                    'BIC: GENEXAMPLE1\n'
                    'Account owner: Organization name \n'
                    'Name of Bank: Professional Banking Institute Ltd.'
                )
            }},
            **kwargs
        )

    @property
    def settings_form_fields(self):
        d = OrderedDict(list(super().settings_form_fields.items()) + [('bank_details', self.form_field_details())])
        d.move_to_end('bank_details', last=False)
        d.move_to_end('_enabled', last=False)
        return d

    def payment_form_render(self, request) -> str:
        template = get_template('pretix_banktransferfi/checkout_payment_form.html')
        ctx = {
            'request': request,
            'event': self.event,
            'details': self.settings.get('bank_details', as_type=LazyI18nString),
        }
        return template.render(ctx)

    def checkout_prepare(self, request, total):
        return True

    def payment_is_valid_session(self, request):
        return True

    def checkout_confirm_render(self, request):
        return self.payment_form_render(request)

    def order_pending_mail_render(self, order) -> str:
        template = get_template('pretix_banktransferfi/email/order_pending.txt')
        ctx = {
            'event': self.event,
            'order': order,
            'details': textwrap.indent(str(self.settings.get('bank_details', as_type=LazyI18nString)), '    '),
            'viitenumero': generate_viitenumero(
                self.event.id,
                ord(order.code[1]),
                order.id
            )
        }
        return template.render(ctx)

    def order_pending_render(self, request, order) -> str:
        template = get_template('pretix_banktransferfi/pending.html')
        ctx = {
            'event': self.event,
            'order': order,
            'details': self.settings.get('bank_details', as_type=LazyI18nString),
            'viitenumero': generate_viitenumero(
                self.event.id,
                ord(order.code[1]),
                order.id
            )
        }
        return template.render(ctx)

    def order_control_render(self, request, order) -> str:
        if order.payment_info:
            payment_info = json.loads(order.payment_info)
        else:
            payment_info = None
        template = get_template('pretix_banktransferfi/control.html')
        ctx = {
            'request': request,
            'event': self.event,
            'payment_info': payment_info,
            'order': order,
            'viitenumero': generate_viitenumero(
                self.event.id,
                ord(order.code[1]),
                order.id
            )
        }
        return template.render(ctx)

    def shred_payment_info(self, order: Order):
        if not order.payment_info:
            return
        d = json.loads(order.payment_info)
        d['reference'] = '█'
        d['payer'] = '█'
        d['_shredded'] = True
        order.payment_info = json.dumps(d)
        order.save(update_fields=['payment_info'])
