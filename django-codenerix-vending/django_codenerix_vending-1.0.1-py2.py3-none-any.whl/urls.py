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

from django.conf.urls import url

from .views import VendingInit
from .views import VendingCreateBudgerForRegisterUser, VendingCreateBudgerForEmployeesUser, VendingCreateBudgerForDefaultUser

"""
from .views import VendingGetPOS, VendingLoadOperators
from .views import VendingStart, Vending, VendingProducts, VendingAddProduct, VendingBasketToOrder, VendingLoadProductSlot, VendingDeleteProduct
from .views import VendingDeleteComanda, VendingCharge, VendingValidateTicket, VendingUpdateProduct, VendingPrintTicket
from .views import VendingPayment, VendingLogin, VendingLogout, VendingSubcategory, VendingPack, VendingPackOption, VendingGetProductPackOption
from .views import VendingHistory, VendingHistoryTicket, VendingHistoryTicketLoad, VendingHistoryTicketPrint
from .views import VendingOpenCashRegister, VendingCashDiary, VendingCashDiaryMovement
from .views import VendingGetFeatureSpecial
"""

urlpatterns = [

    url(r'^vending$', VendingInit.as_view(), name='CDNX_vending_init'),
    url(r'^sale_registered_users$', VendingCreateBudgerForRegisterUser.as_view(), name='CDNX_vending_sale_resgistered_user'),
    url(r'^sale_default_users$', VendingCreateBudgerForDefaultUser.as_view(), name='CDNX_vending_sale_default_user'),
    url(r'^sale_employees_users$', VendingCreateBudgerForEmployeesUser.as_view(), name='CDNX_vending_sale_employees_user'),

]
"""
urlpatterns = [
    url(r'^vendinggetpos$', VendingGetPOS.as_view(), name='CDNX_vending_get_pos'),

    url(r'^vending-login$', VendingLogin.as_view(), name='CDNX_vending_login'),
    url(r'^vending-logout$', VendingLogout.as_view(), name='CDNX_vending_logout'),
    url(r'^vending_load_operators$', VendingLoadOperators.as_view(), name='CDNX_vending_load_operators'),
    url(r'^vending-cashdiary$', VendingCashDiary.as_view(), name='CDNX_vending_cashdiary'),
    url(r'^vending-cashdiary-movement$', VendingCashDiaryMovement.as_view(), name='CDNX_vending_cashdiary_movement'),

    url(r'^vending-start$', VendingStart.as_view(), name='CDNX_vending_start'),
    url(r'^vending/(?P<pk>\w+)$', Vending.as_view(), name='CDNX_vending'),
    url(r'^vending-charge/(?P<pk>\w+)$', VendingCharge.as_view(), name='CDNX_vending_charge'),
    url(r'^vending-history$', VendingHistory.as_view(), name='CDNX_vending_history'),

    url(r'^vendingproducts$', VendingProducts.as_view(), name='CDNX_vending_products'),
    url(r'^vendingsubcategory$', VendingSubcategory.as_view(), name='CDNX_vending_subcategory'),
    url(r'^vendingpack$', VendingPack.as_view(), name='CDNX_vending_pack'),
    url(r'^vendingpackoption$', VendingPackOption.as_view(), name='CDNX_vending_packoption'),
    url(r'^vendinggetpackoption$', VendingGetProductPackOption.as_view(), name='CDNX_vending_get_packoption'),
    url(r'^vendinggetfeaturespecial$', VendingGetFeatureSpecial.as_view(), name='CDNX_vending_get_feature_special'),


    url(r'^vendingaddproduct$', VendingAddProduct.as_view(), name='CDNX_vending_products_add'),
    url(r'^vendingbaskettoorder$', VendingBasketToOrder.as_view(), name='CDNX_vending_basket_to_order'),
    url(r'^vendingloadproductslot$', VendingLoadProductSlot.as_view(), name='CDNX_vending_load_product_slot'),
    url(r'^vendingdeleteproduct/(?P<pk>\w+)$', VendingDeleteProduct.as_view(), name='CDNX_vending_products_delete'),
    url(r'^vendingupdateproduct/(?P<pk>\w+)$', VendingUpdateProduct.as_view(), name='CDNX_vending_products_update'),
    url(r'^vendingdeletecomanda/(?P<pk>\w+)$', VendingDeleteComanda.as_view(), name='CDNX_vending_products_comanda'),
    url(r'^vendingvalidateticket/(?P<pk>\w+)$', VendingValidateTicket.as_view(), name='CDNX_vending_validate_ticket'),
    url(r'^vendingprintticket/(?P<pk>\w+)$', VendingPrintTicket.as_view(), name='CDNX_vending_print_ticket'),
    url(r'^vendingopencashregister/(?P<pk>\w+)$', VendingOpenCashRegister.as_view(), name='CDNX_vending_open_cash_register'),

    url(r'^vendingpayment$', VendingPayment.as_view(), name='CDNX_vending_payment'),

    url(r'^vendinghistoryticket$', VendingHistoryTicket.as_view(), name='CDNX_vending_history_ticket'),
    url(r'^vendinghistoryticketload$', VendingHistoryTicketLoad.as_view(), name='CDNX_vending_load_ticket_history'),
    url(r'^vendinghistoryticketprint$', VendingHistoryTicketPrint.as_view(), name='CDNX_vending_print_ticket_history'),
    
]
"""