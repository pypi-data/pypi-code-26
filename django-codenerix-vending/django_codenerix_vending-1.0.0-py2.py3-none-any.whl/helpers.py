# -*- coding: utf-8 -*-
#
# django-codenerix-vending
#
# Copyright 2018 Centrologic Computational Logistic Center S.L.
#
# Project URL : http://www.codenerix.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import datetime

from django.db.models import F, Q
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.conf import settings

from codenerix.middleware import get_current_user
from codenerix_extensions.helpers import get_language_database
from codenerix_invoicing.models_cash import CashDiary
from codenerix_invoicing.models_sales import SalesBasket, ROLE_BASKET_SHOPPINGCART, SalesLines
# SalesLineBasket, SalesLineTicket, 
from codenerix_invoicing.models_sales import SalesTicket, ReasonModification
from codenerix_pos.models import POSSlot, POSHardware, KIND_POSHARDWARE_TICKET, POS, POSOperator
from codenerix_products.models import Category, ProductFinal, TypeTax


class CodenerixVending(object):

    def __init__(self, request):
        self.request = request

    def printer_ticket(self, PDV, request, ticket_obj, comanda=None):
        context = {}
        printer = POSHardware.objects.filter(
            kind=KIND_POSHARDWARE_TICKET,
            poss=PDV
        ).first()
        if printer:
            config = printer.get_config()
            column = config.get('column', 48)
            cut = config.get('cut', False)

            num_impressions = ticket_obj.print_counter(get_current_user())
            context_hardware = self.create_ticket_to_print(request, ticket_obj, num_impressions, comanda, column, cut)
            printer.send(context_hardware)
            context = context_hardware
            context = {'msg': 'OK'}
        else:
            context = {'error': _('Printer do not found')}
        return context

    def create_ticket_to_print(self, request, ticket_obj, num_impressions=None, comanda=None, column=48, cut=False):
        template_name = 'vendings/ticket.html'
        context_hardware = {}

        lines = SalesLines.objects.filter(
            ticket=ticket_obj,
            quantity__gt=0,
            removed=False
        ).all()
        info = ticket_obj.calculate_price_doc_complete()
        prices = info.copy()
        taxes = {}
        for tax in info['taxes']:
            name = TypeTax.objects.filter(tax=tax).first()
            if name is None:
                name = tax
            taxes[name] = info['taxes'][tax]
        prices['taxes'] = taxes
        LINEA = u"-" * column

        just = column - 7 - 8 - 5  # quantity, amount, margin
        ctx = {
            'labels': {
                'cant': 'Cant',
                'product': 'Producto',
                'price': 'Precio'
            },
            'cut': cut,
            'ticket': ticket_obj,
            'lines': lines,
            'prices': prices,
            'LINEA': LINEA,
            'comanda': comanda,
            'config': {
                'cant': {
                    'slice': ":{}".format(7),
                    'just': 7,
                },
                'product': {
                    'slice': ":{}".format(just),
                    'just': just,
                },
                'price': {
                    'slice': ":{}".format(8),
                    'just': 8,
                },
                'subtotal': {
                    'slice': ":{}".format(column - 9),
                    'just': column - 9,
                },
                'tax_porc': {
                    'slice': ":{}".format(15),
                    'just': 15,
                },
                'tax': {
                    'slice': ":{}".format(column - 22),
                    'just': column - 16,
                },
                'total': {
                    'slice': ":{}".format(column - 6),
                    'just': column - 6,
                },
            }
        }

        rendering = render(request, template_name, ctx)
        context_hardware['template'] = rendering._container[0].decode("utf-8")
        if ticket_obj.lock is False:
            filename = "logo_ticket_cif.png"
            datas = None
        elif num_impressions > 1:
            filename = "logo_ticket_cif_reprinter.png"
            datas = 'info_fiscal.png'
        elif num_impressions == 1:
            filename = "logo_ticket_cif.png"
            datas = 'info_fiscal.png'

        File = open("{}img/{}".format(settings.STATIC_ROOT, filename), "rb")
        logo = base64.b64encode(File.read()).decode()
        context_hardware['ctx'] = {
            'logo': ['image', logo],
        }
        File.close()
        if datas:
            File = open("{}img/{}".format(settings.STATIC_ROOT, datas), "rb")
            dataf = base64.b64encode(File.read()).decode()
            File.close()
            context_hardware['dataf'] = ['image', dataf]
        else:
            dataf = None

        """
        if not comanda:
            context_hardware['ctx']['barcode'] = ['barcode', {
                'code': str(ticket_obj.code).zfill(13),
                'bc': 'EAN13',
                'height': 64,
                'width': 3,
                'pos': u'BELOW',
                'font': u'A',
                'align_ct': True,
                'function_type': None
            }, ]
        """
        return context_hardware

    def get_POS(self):
        uuid = self.request.session.get('POS_client_UUID', None)
        pos = POS.objects.filter(uuid=uuid).first()
        if pos:
            return {'uuid': str(pos.uuid), "POS": pos}
        else:
            return {'uuid': '', "POS": None}

    def get_lang(self):
        return get_language_database()

    def get_categories(self):
        PDV = self.get_POS()['POS']
        lang = self.get_lang()

        qs = Category.objects.filter(**{
            'show_menu': True,
            'products__products_final__posproducts__group_product__poss': PDV,
            'products__products_final__{}__public'.format(lang): True
        }).values(
            'pk', '{}__name'.format(lang)
        ).annotate(
            name=F('{}__name'.format(lang))
        ).order_by("order").distinct()

        return qs

    def get_shoppingcarts(self, paid=False, slot=None, without_order=False):
        PDV = self.get_POS()['POS']

        qs = SalesBasket.objects.filter(
            pos_slot__zone__poss=PDV,
            role=ROLE_BASKET_SHOPPINGCART,
            removed=False
        )
        if not paid:
            qs = qs.filter(
                Q(order_sales__isnull=True)
                |
                Q(
                    order_sales__payment__isnull=True,
                    order_sales__cash_movements__isnull=True,
                    order_sales__removed=False,
                )
            )
        if slot:
            qs = qs.filter(
                pos_slot__pk=slot,
            )
        if without_order:
            qs = qs.filter(
                order_sales__isnull=True,
            )
        return qs

    def get_last_shoppingcarts(self, slot_pk):
        qs = self.get_shoppingcarts(paid=False).filter(
            pos_slot__pk=slot_pk,
        ).last()
        return qs

    def get_lines_shoppingcart(self, slot_pk):
        qs = SalesLines.objects.filter(
            basket__pos_slot__pk=slot_pk,
            basket__order_sales__payment__isnull=True,
            basket__order_sales__cash_movements__isnull=True,
            basket__role=ROLE_BASKET_SHOPPINGCART,
            quantity__gt=0,
            removed=False,
            basket__removed=False
        ).annotate(
            xorder=F('basket__order_sales')
        ).order_by(
            'pk'
        )
        return qs

    def get_products_pack(self):
        lang = self.get_lang()
        PDV = self.get_POS()['POS']

        qs = ProductFinal.objects.filter(
            Q(**{
                '{}__public'.format(lang): True,
                'productfinals_option__isnull': False,
                'posproducts__group_product__poss': PDV,
            }),
        ).distinct().annotate(
            name=F("{}__name".format(lang))
        )
        return qs

    def get_slots(self):
        PDV = self.get_POS()['POS']
        qs = POSSlot.objects.filter(zone__poss=PDV)
        return qs

    def get_hardware(self, kind):
        PDV = self.get_POS()['POS']
        qs = POSHardware.objects.filter(
            pos=PDV,
            kind=kind,
            enable=True
        ).first()
        return qs

    def get_reasons_modification(self):
        qs = ReasonModification.objects.filter(enable=True).order_by('code')
        return qs

    def get_operators(self):
        context = {}
        PDV = self.get_POS()['POS']
        if PDV:
            opts = POSOperator.objects.filter(
                pos=PDV, enable=True
            )
            operators = []
            for operator in opts:
                operators.append({
                    'pk': operator.pk,
                    'name': operator.external.user.__str__(),
                    'user': operator.external.user.username
                })
            context['operators'] = operators
        else:
            context['error'] = _("POS not registered or can not be identified, plese make sure that POSClient is running")
        return context

    def get_ticket(self, ticket_pk):
        PDV = self.get_POS()['POS']
        ticket = SalesTicket.objects.filter(
            pk=ticket_pk,
            removed=False,
            line_ticket_sales__removed=False,
            line_ticket_sales__line_order__removed=False,
            line_ticket_sales__line_order__order__removed=False,
            line_ticket_sales__line_order__order__budget__removed=False,
            line_ticket_sales__line_order__order__budget__pos_slot__zone__poss=PDV
        ).first()
        return ticket

    def reprinter_ticket(self, ticket_pk, request):
        context = {}
        PDV = self.get_POS()['POS']
        ticket = self.get_ticket(ticket_pk)

        if not ticket:
            context['error'] = _("Ticket invalid")
        else:
            context.update(self.printer_ticket(PDV, request, ticket))
        return context

    def get_info_ticket(self, ticket_pk):
        context = {}
        ticket = self.get_ticket(ticket_pk)

        if not ticket:
            context['error'] = _("Ticket invalid")
        else:
            context['code'] = ticket.code
            products = []
            for line in ticket.line_ticket_sales.filter(quantity__gt=0):
                tmp = {}
                tmp['quantity'] = line.quantity
                tmp['price'] = float(line.total)
                tmp['description'] = line.description.__str__()
                if line.line_order.line_order_option_sales.exists():
                    tmp['more'] = []
                    for opt in line.line_order.line_order_option_sales.all().order_by('product_option__order'):
                        tmp['more'].append({
                            'quantity': opt.quantity,
                            'product': opt.product_final.__str__()
                        })
                else:
                    tmp['more'] = None
                products.append(tmp)

            context['products'] = products

            totales = {}
            prices = ticket.calculate_price_doc_complete()
            if 'discounts' in totales:
                totales['discounts'] = [{x: float(prices['discounts'][x])} for x in prices['discounts'].keys()][0]
            else:
                totales['discounts'] = {}
            if 'equivalence_surcharges' in totales:
                totales['equivalence_surcharges'] = [{x: float(prices['equivalence_surcharges'][x])} for x in prices['equivalence_surcharges'].keys()][0]
            else:
                totales['equivalence_surcharges'] = {}
            if 'taxes' in totales:
                totales['taxes'] = [{x: float(prices['taxes'][x])} for x in prices['taxes'].keys()][0]
            else:
                totales['taxes'] = {}
            totales['subtotal'] = float(prices['subtotal'])
            totales['total'] = float(prices['total'])

            context['totales'] = totales
        return context

    def get_history_tickets(self, slot_pk, date_ini, date_end):
        context = {
            'error': None,
            'tickets': [],
        }
        PDV = self.get_POS()['POS']

        if slot_pk:
            slot = POSSlot.objects.filter(pk=slot_pk, zone__poss=PDV).first()
        else:
            slot = None
        if slot:
            tickets = SalesTicket.objects.filter(
                line_ticket_sales__line_order__order__budget__pos_slot=slot,
                removed=False,
                line_ticket_sales__line_order__order__budget__removed=False,
                line_ticket_sales__line_order__order__removed=False,
                line_ticket_sales__line_order__removed=False,
                line_ticket_sales__removed=False,
                date__range=(
                    datetime.datetime.combine(date_ini, datetime.time.min),
                    datetime.datetime.combine(date_end, datetime.time.max)
                )
            ).order_by('-pk').distinct()
            for ticket in tickets:
                context['tickets'].append({
                    'pk': ticket.pk,
                    'code': ticket.code,
                    'total': float(ticket.total),
                })

        else:
            context['error'] = _("Slot invalid")

        return context

    def cashdiary_isopen(self):
        PDV = self.get_POS()['POS']
        opened = CashDiary.objects.filter(pos=PDV, closed_user__isnull=True).first()
        return bool(opened)
