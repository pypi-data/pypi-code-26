# -*- coding: utf-8 -*-
#
# This file is part of fedscm_admin.
# Copyright © 2018 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
"""
Provides helper functions around requests
"""
from __future__ import absolute_import
import json

import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectTimeout, ConnectionError
import click

from fedscm_admin.config import get_config_item
from fedscm_admin import CONFIG, VERSION


def retry_session():
    session = requests.Session()
    retry = Retry(
        total=5,
        read=5,
        connect=5,
        backoff_factor=1,
        status_forcelist=(400, 500, 502, 504),
        method_whitelist=('GET', 'POST', 'PATCH'),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def requests_wrapper(*args, **kwargs):
    """
    A wrapper around the requests module with error handling
    :param args: Any positional arguments you'd pass to a requests function
    :param kwargs: Any keyword arguments you'd pass to a requests function.
    Additionally, there are special parameters used such as "service_name",
    which is a string used in any error messages, and "http_verb", which
    specifies what action to take on the API. If it's not set, it will default
    to "get".
    :return: a requests object
    """
    session = retry_session()

    if 'service_name' in kwargs:
        service_name = kwargs.pop('service_name')
    else:
        service_name = 'unknown'

    if 'http_verb' in kwargs:
        action = kwargs.pop('http_verb').lower()
    else:
        action = 'get'

    # If the request is JSON and a dict was passed in as the payload, then
    # convert the string to JSON
    if 'data' in kwargs and isinstance(kwargs['data'], dict) \
            and 'headers' in kwargs and isinstance(kwargs['headers'], dict) \
            and 'json' in kwargs['headers'].get('Content-Type'):
        kwargs['data'] = json.dumps(kwargs['data'])

    user_agent = {'User-Agent': 'fedscm-admin/{0}'.format(VERSION)}
    if 'headers' in kwargs:
        kwargs['headers'].update(user_agent)
    else:
        kwargs['headers'] = user_agent

    requests_function = getattr(session, action)

    try:
        return requests_function(*args, **kwargs)
    except (ConnectionError, ConnectTimeout) as e:
        if service_name is not None:
            error_msg = ('Could not connect to "{0}" at {1}. Please try again.'
                         .format(service_name, e.request.url))
        else:
            error_msg = ('Could not connect to a required service at {1}. '
                         'Please try again.'.format(e.request.url))
        raise click.ClickException(error_msg)


def get_request_json(rv, action, error_key=None):
    """
    A wrapper to get the JSON from a request object.
    :param rv: a request object (e.g. return value of requests.get)
    :param action: a string describing the action for more useful error
    messages
    :param error_key: a string of the key that holds the error message in the
    JSON body. If this is set to None, the whole JSON will be used as the
    error message.
    :return: dictionary of the returned JSON or a ClickException
    """
    base_error_msg = (
        'A failure occurred while {0} at {1}. The status code was "{2}".')
    if rv.ok:
        return rv.json()
    elif rv.status_code == 500:
        # There will be no JSON with an error message here
        error_msg = base_error_msg.format(
            action, rv.request.url, rv.status_code)
        raise click.ClickException(error_msg)
    else:
        # If it's not a 500 error, we can assume that the API returned an error
        # message in JSON that we can log
        try:
            rv_error = rv.json()
            if error_key is not None:
                rv_error = rv_error.get(error_key)
        except ValueError:
            rv_error = ''
        error_msg = base_error_msg.format(
            action, rv.request.url, rv.status_code)
        error_msg = '{0} The error was "{1}".'.format(error_msg, rv_error)
        if rv.status_code == 401 and 'token' in rv_error:
            error_msg = ('{0} The token is stored in '
                         '"~/.config/fedscm-admin/config.ini" or '
                         '"/etc/fedscm-admin/config.ini".'.format(error_msg))
        raise click.ClickException(error_msg)


def get_auth_header(service):
    """
    Get the HTTP header with authorization for the desired service.
    :param service: a string of the service the authorization header is for
    :return: a dictionary of the HTTP header
    """
    api_token = get_config_item(CONFIG, '{0}_api_token'.format(service))
    prefix = 'token' if service.startswith('pagure') else 'Token'
    return {
        'Authorization': '{0} {1}'.format(prefix, api_token),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
