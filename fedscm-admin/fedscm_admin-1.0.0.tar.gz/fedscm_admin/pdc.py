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
PDC API helper functions
"""
from __future__ import absolute_import
from six.moves.urllib.parse import urlencode

import click

from fedscm_admin import CONFIG
from fedscm_admin.config import get_config_item
from fedscm_admin.request_utils import (
    requests_wrapper, get_request_json, get_auth_header)
from fedscm_admin.exceptions import ValidationError


def get_pdc_auth_header():
    """
    Get a dictionary of the headers needed to make an authenticated API
    call to PDC
    :return: a dictionary of the headers needed to make an authenticated API
    call to PDC
    """
    return get_auth_header('pdc')


def get_global_component(global_component_name):
    """
    Get the Global Component entry in PDC
    :param global_component_name: a string of the Global Component to search
    for
    :return: a dictionary describing the Global Component
    """
    pdc_url = get_config_item(CONFIG, 'pdc_url')
    query_args = urlencode({'name': global_component_name})
    pdc_component_gc_url = ('{0}/rest_api/v1/global-components/?{1}'
                            .format(pdc_url.rstrip('/'), query_args))
    rv = requests_wrapper(
        pdc_component_gc_url, timeout=60, service_name='PDC')
    rv_json = get_request_json(rv, 'getting a global component in PDC')
    if rv_json['count'] == 0:
        return None
    else:
        return rv_json['results'][0]


def get_branch(global_component, branch, branch_type):
    """
    Get a branch in PDC
    :param global_component: a string of the Global Component the branch
    belongs to
    :param branch: a string of the branch name to search for
    :param branch_type: a string of the branch type to search for (e.g. rpm,
    module, etc.)
    :return: a dictionary of the branch in PDC
    """
    pdc_url = get_config_item(CONFIG, 'pdc_url')
    pdc_component_branch_url = \
        '{0}/rest_api/v1/component-branches/'.format(pdc_url.rstrip('/'))
    query_args = urlencode({
        'global_component': global_component,
        'name': branch,
        'type': branch_type
    })
    pdc_component_branch_url_with_query = \
        '{0}?{1}'.format(pdc_component_branch_url, query_args)

    rv = requests_wrapper(
        pdc_component_branch_url_with_query, timeout=60, service_name='PDC')
    rv_json = get_request_json(rv, 'getting a branch in PDC')
    if rv_json['count'] == 0:
        return None
    else:
        return rv_json['results'][0]


def new_global_component(global_component_name, pagure_web_url):
    """
    Create a new Global Component entry in PDC
    :param global_component_name: a string of the Global Component to create
    :param pagure_web_url: a string of the web URL to the project in Pagure
    :return: a dictionary of the returned JSON after creation or if it already
    exists, then a dictionary of the existing Global Component
    """
    pdc_url = get_config_item(CONFIG, 'pdc_url')
    pdc_component_gc_url = ('{0}/rest_api/v1/global-components/'
                            .format(pdc_url.rstrip('/')))
    click.echo('- Checking for PDC global-component {0}'.format(
        global_component_name))
    existing_gc = get_global_component(global_component_name)
    if existing_gc is not None:
        return existing_gc

    headers = get_pdc_auth_header()
    payload = {
        'name': global_component_name,
        'dist_git_web_url': pagure_web_url
    }

    click.echo('- Creating PDC global-component {0}'.format(
        global_component_name))
    rv = requests_wrapper(
        pdc_component_gc_url, data=payload, headers=headers, timeout=60,
        http_verb='post', service_name='PDC')

    return get_request_json(rv, 'creating a new global component in PDC')


def new_branch(global_component, branch, branch_type):
    """
    Create a new branch in PDC
    :param global_component: a string of the Global Component the new branch
    belongs to
    :param branch: a string of the name of the branch to create
    :param branch_type: a string of the type of branch to create (e.g. rpm,
    module, etc.)
    :return: None
    """
    pdc_url = get_config_item(CONFIG, 'pdc_url')
    pdc_component_branch_url = \
        '{0}/rest_api/v1/component-branches/'.format(pdc_url.rstrip('/'))

    click.echo('- Checking for existing PDC branch ({0}){1}#{2}'.format(
        branch_type, global_component, branch))
    existing_branch = get_branch(global_component, branch, branch_type)
    if existing_branch is not None:
        if existing_branch['slas']:
            raise ValidationError(
                'The PDC branch already exists and has SLAs tied to it')
        else:
            # The branch exists, but no SLAs are tied to it, so it's the same
            # as if a new branch was just created
            return None

    headers = get_pdc_auth_header()
    payload = {
        'global_component': global_component,
        'name': branch,
        'type': branch_type
    }

    click.echo('- Creating PDC branch ({0}){1}#{2}'.format(
        branch_type, global_component, branch))
    rv = requests_wrapper(
        pdc_component_branch_url, data=payload, headers=headers, timeout=60,
        http_verb='post', service_name='PDC')
    get_request_json(rv, 'creating a new branch in PDC')


def new_sla_to_branch(sla, eol, global_component, branch, branch_type):
    """
    Create a new SLA to branch mapping
    :param sla: a string of the SLA name
    :param eol: a string of the EOL in the format of "2020-01-01"
    :param global_component: a string of the Global Component that the branch
    belongs to
    :param branch: a string of the name of the branch
    :param branch_type: a string of the branch type (e.g. rpm, module, etc.)
    :return: None
    """
    pdc_url = get_config_item(CONFIG, 'pdc_url')
    pdc_component_branch_url = \
        '{0}/rest_api/v1/component-branch-slas/'.format(pdc_url.rstrip('/'))

    headers = get_pdc_auth_header()
    payload = {
        'sla': sla,
        'eol': eol,
        'branch': {
            'global_component': global_component,
            'name': branch,
            'type': branch_type
        }
    }

    click.echo('- Mapping SL {0}:{1} to ({2}){3}#{4}'.format(
        sla, eol, branch_type, global_component, branch))
    rv = requests_wrapper(
        pdc_component_branch_url, data=payload, headers=headers,
        timeout=60, http_verb='post', service_name='PDC')
    get_request_json(rv, 'creating a new SLA in PDC')
    return None


def get_sla(sla_name):
    """
    Gets the SLA from PDC
    :param sla_name: a string of the SLA name
    :return: a dictionary representing the SLA or None
    """
    pdc_url = get_config_item(CONFIG, 'pdc_url').rstrip('/')
    pdc_api_url = '{0}/rest_api/v1/component-sla-types/'.format(pdc_url)
    query_args = urlencode({'name': sla_name})
    pdc_api_url_with_args = '{0}?{1}'.format(pdc_api_url, query_args)
    rv = requests_wrapper(
        pdc_api_url_with_args, timeout=60, service_name='PDC')
    rv_json = get_request_json(rv, 'getting an SLA', 'error')
    if rv_json['count'] == 1:
        return rv_json['results']
    else:
        return None


def component_type_to_singular(component_type):
    """
    Converts a component_type to its singular form
    :param component_type: a string representing the component type to be made
    singular.
    :return: a string containing the singular version of the component_type
    """
    return component_type.strip().rstrip('s')
