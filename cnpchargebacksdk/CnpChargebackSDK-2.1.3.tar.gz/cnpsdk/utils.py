# -*- coding: utf-8 -*-
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

from __future__ import absolute_import, print_function, unicode_literals

import json
import os
import pyxb
import xmltodict
from cnpsdk import fields_chargeback

from . import version


class Configuration(object):
    """Setup Configuration variables.

    Attributes:
        user (Str): authentication.user
        password (Str): authentication.password
        merchant_id (Str): The unique string to identify the merchant within the system.
        url (Str): Url for server.
        proxy (Str): Https proxy server address. Must start with "https://"
        print_xml (Str): Whether print request and response xml
    """
    VERSION = version.VERSION
    RELEASE = version.RELEASE
    _CONFIG_FILE_PATH = os.path.join(os.environ['CNP_CHARGEBACK_SDK_CONFIG'], ".cnp_chargeback_sdk.conf") \
        if 'CNP_CHARGEBACK_SDK_CONFIG' in os.environ else os.path.join(os.path.expanduser("~"), ".cnp_chargeback_sdk.conf")

    def __init__(self, conf_dict=dict()):
        attr_dict = {
            'username': '',
            'password': '',
            'merchant_id': '',
            'url': 'http://www.testvantivcnp.com/sandbox/new',
            'proxy': '',
            'print_xml': False,
            'neuter_xml': False,
        }

        # set default values
        for k in attr_dict:
            setattr(self, k, attr_dict[k])

        # override values by loading saved conf
        try:
            with open(self._CONFIG_FILE_PATH, 'r') as config_file:
                config_json = json.load(config_file)
                for k in attr_dict:
                    if k in config_json and config_json[k]:
                        setattr(self, k, config_json[k])
        except:
            # If get any exception just pass.
            pass

        # override values by args
        if conf_dict:
            for k in conf_dict:
                if k in attr_dict:
                    setattr(self, k, conf_dict[k])
                else:
                    raise ChargebackError('"%s" is NOT an attribute of conf' % k)

    def save(self):
        """Save Class Attributes to .cnp_chargeback_sdk.conf

        Returns:
            full path for configuration file.

        Raises:
            IOError: An error occurred
        """
        with open(self._CONFIG_FILE_PATH, 'w') as config_file:
            json.dump(vars(self), config_file)
        return self._CONFIG_FILE_PATH


def obj_to_xml(obj):
    """Convert object to xml string without namespaces

    Args:
        obj: Object

    Returns:
        Xml string

    Raises:
        pyxb.ValidationError
    """
    # TODO convert object to xml without default namespace gracefully.
    try:

        xml = obj.toxml('utf-8')
    except pyxb.ValidationError as e:
        raise ChargebackError(e.details())
    xml = xml.replace(b'ns1:', b'')
    xml = xml.replace(b':ns1', b'')
    return xml


def generate_retrieval_response(http_response, return_format='dict'):
    return convert_to_format(http_response.text, "chargebackRetrievalResponse", return_format)


def generate_update_response(http_response, return_format='dict'):
    return convert_to_format(http_response.text, "chargebackUpdateResponse", return_format)


def generate_document_response(http_response, return_format='dict'):
    return convert_to_format(http_response.text, "chargebackDocumentUploadResponse", return_format)


def generate_error_response(http_response, return_format='dict'):
    return convert_to_format(http_response.text, "errorResponse", return_format)


def convert_to_format(http_response, response_type, return_format='dict'):
    return_format = return_format.lower()
    if return_format == 'xml':
        response_xml = http_response.text
        return response_xml
    elif return_format == 'object':
        return convert_to_obj(http_response.text)
    else:
        return convert_to_dict(http_response, response_type)


def convert_to_obj(xml_response):
    return fields_chargeback.CreateFromDocument(xml_response)


def convert_to_dict(xml_response, response_type):
    response_dict = xmltodict.parse(xml_response)[response_type]
    if response_dict['@xmlns'] != "":
        _create_lists(response_dict)
        return response_dict
    else:
        raise ChargebackError("Invalid Format")


def _create_lists(response_dict):
    if "chargebackCase" in response_dict:
        _create_list("chargebackCase", response_dict)

        for case in response_dict["chargebackCase"]:
            if "activity" in case:
                _create_list("activity", case)

    if "errors" in response_dict:
        _create_list("error", response_dict["errors"])


# if there is only one element for the given key in container, create a list for it
def _create_list(element_key, container):
    element_value = container[element_key]
    if element_value != "" and not isinstance(element_value, list):
        container[element_key] = [element_value]


class ChargebackError(Exception):

    def __init__(self, message):
        self.message = message


class ChargebackWebError(Exception):

    def __init__(self, message, code, error_list=None):
        self.message = message
        self.code = code
        self.error_list = error_list


class ChargebackDocumentError(Exception):

    def __init__(self, message, code):
        self.message = message
        self.code = code
