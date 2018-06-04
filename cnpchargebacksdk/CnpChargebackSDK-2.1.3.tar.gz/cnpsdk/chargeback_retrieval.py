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

from cnpsdk import (utils, communication)

conf = utils.Configuration()

SERVICE_ROUTE = "/chargebacks"

"""
/////////////////////////////////////////////////////
            ChargebackRetrieval API:
/////////////////////////////////////////////////////
"""


def get_chargeback_by_case_id(case_id, config=conf):
    url_suffix = SERVICE_ROUTE + "/" + case_id
    return communication.http_get_retrieval_request(url_suffix, config)


def get_chargebacks_by_token(token, config=conf):
    return _get_retrieval_response({"token": token}, config)


def get_chargebacks_by_card_number(card_number, expiration_date, config=conf):
    return _get_retrieval_response({"cardNumber": card_number, "expirationDate": expiration_date}, config)


def get_chargebacks_by_arn(arn, config=conf):
    return _get_retrieval_response({"arn": arn}, config)


def get_chargebacks_by_date(activity_date, config=conf):
    return _get_retrieval_response({"date": activity_date}, config)


def get_chargebacks_by_financial_impact(activity_date, financial_impact, config=conf):
    return _get_retrieval_response({"date": activity_date, "financialOnly": financial_impact}, config)


def get_actionable_chargebacks(actionable, config=conf):
    return _get_retrieval_response({"actionable": actionable}, config)


"""
/////////////////////////////////////////////////////
"""


def _get_retrieval_response(parameters, config):
    url_suffix = SERVICE_ROUTE
    prefix = "?"

    for name in parameters:
        url_suffix += prefix + name + "=" + str(parameters[name])
        prefix = "&"

    return communication.http_get_retrieval_request(url_suffix, config)