# -*- coding: utf-8 -*-l
# Copyright (c) 2017 Vantiv eCommerce
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
from __future__ import absolute_import, print_function, unicode_literals

from cnpsdk import (fields_chargeback, utils, communication)

conf = utils.Configuration()

SERVICE_ROUTE = "/chargebacks"


"""
/////////////////////////////////////////////////////
            ChargebackUpdate API:
/////////////////////////////////////////////////////
"""


def assign_case_to_user(case_id, user_id, note, config=conf):
    request_body = fields_chargeback.chargebackUpdateRequest()
    request_body.activityType = "ASSIGN_TO_USER"
    request_body.assignedTo = user_id
    request_body.note = note
    return _get_update_response(case_id, request_body, config)


def add_note_to_case(case_id, note, config=conf):
    request_body = fields_chargeback.chargebackUpdateRequest()
    request_body.activityType = "ADD_NOTE"
    request_body.note = note
    return _get_update_response(case_id, request_body, config)


def assume_liability(case_id, note, config=conf):
    request_body = fields_chargeback.chargebackUpdateRequest()
    request_body.activityType = "MERCHANT_ACCEPTS_LIABILITY"
    request_body.note = note
    return _get_update_response(case_id, request_body, config)


def represent_case(case_id, note, representment_amount=None, config=conf):
    request_body = fields_chargeback.chargebackUpdateRequest()
    request_body.activityType = "MERCHANT_REPRESENT"
    request_body.note = note
    request_body.representedAmount = representment_amount
    return _get_update_response(case_id, request_body, config)


def respond_to_retrieval_request(case_id, note, config=conf):
    request_body = fields_chargeback.chargebackUpdateRequest()
    request_body.activityType = "MERCHANT_RESPOND"
    request_body.note = note
    return _get_update_response(case_id, request_body, config)
    

def request_arbitration(case_id, note, config=conf):
    request_body = fields_chargeback.chargebackUpdateRequest()
    request_body.activityType = "MERCHANT_REQUESTS_ARBITRATION"
    request_body.note = note
    return _get_update_response(case_id, request_body, config)


"""
/////////////////////////////////////////////////////
"""


def _get_update_response(parameter_value1, request_body, config):
    url_suffix = SERVICE_ROUTE + "/" + str(parameter_value1)
    return communication.http_put_request(url_suffix, request_body, config)

