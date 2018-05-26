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
import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.urls import reverse
from django.views.generic import View
from django.forms.utils import ErrorList

from codenerix.views import GenCreateModal, GenCreate

from codenerix_invoicing.models import BillingSeries
from codenerix_invoicing.models_cash import CashDiary
from codenerix_invoicing.models_sales import SalesBasket, Customer
from codenerix_pos.models import POS
from .forms import BudgetForRegiterUserForm, BudgetForEmployeesUserForm


class VendingInit(View):
    template_name = 'vendings/init.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {}

        uuid = self.request.session.get('POS_client_UUID', None)
        opened = CashDiary.objects.filter(pos__uuid=uuid, closed_user__isnull=True).first()

        if opened is None:
            context['error'] = _("No CashDiary is open!")
        context['ws_entry_point'] = 'vendings'
        context['url_budget'] = reverse('CDNX_invoicing_salesbaskets_shoppingcart_vending_list', kwargs={'bpk': 'CNDX_VENDING_LINES'})

        return render(request, self.template_name, context)


class VendingCreateBudgerForRegisterUser(GenCreateModal, GenCreate):
    model = SalesBasket
    form_class = BudgetForRegiterUserForm

    def form_valid(self, form):
        bs = BillingSeries.objects.filter(default=True).first()
        if bs is None:
            errors = form._errors.setdefault("customer", ErrorList())
            errors.append(_('Billing Series by default not exists'))
            return self.form_invalid(form)
        else:
            self.request.billing_series = bs
            form.instance.billing_series = bs

            self.request.name = "{}".format(datetime.datetime.now())
            form.instance.name = "{}".format(datetime.datetime.now())

            self.request.signed = True
            form.instance.signed = True
            
            uuid = self.request.session.get('POS_client_UUID', None)
            pos = POS.objects.filter(uuid=uuid).first()

            self.request.pos = pos
            form.instance.pos = pos

        return super(VendingCreateBudgerForRegisterUser, self).form_valid(form)


class VendingCreateBudgerForEmployeesUser(VendingCreateBudgerForRegisterUser):
    form_class = BudgetForEmployeesUserForm


class VendingCreateBudgerForDefaultUser(View):
    def post(self, request, *args, **kwargs):
        answer = {}
        # falta el pos
        bs = BillingSeries.objects.filter(default=True).first()
        customer_default = Customer.objects.filter(default_customer=True).first()
        if bs is None:
            answer['error'] = _('Billing Series by default not exists')
        elif customer_default is None:
            answer['error'] = _('Customer by default not exists')
        else:
            budget = SalesBasket()
            budget.billing_series = bs
            budget.name = "{}".format(datetime.datetime.now())
            budget.signed = True
            budget.customer = customer_default
            uuid = self.request.session.get('POS_client_UUID', None)
            pos = POS.objects.filter(uuid=uuid).first()

            budget.pos = pos

            budget.save()
            answer['__pk__'] = budget.pk

        return JsonResponse(answer)
