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
The fedscm-admin script
"""
from __future__ import absolute_import

import click

from fedscm_admin.utils import (
    process_all_tickets, list_all_tickets, process_ticket,
    login_to_bugzilla_with_user_input, login_to_fas_with_user_input)
import fedscm_admin.pagure
import fedscm_admin.config
from fedscm_admin import CONFIG

ACTION_CHOICES = ['list', 'process', 'processall']


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option('--force', '-f', is_flag=True,
              help='Skips Bugzilla bug validation')
@click.option('--auto-approve/--no-auto-approve', default=False,
              help=('Automatically approve tickets that don\'t need '
                    'approval.'))
@click.argument('action', type=click.Choice(ACTION_CHOICES))
@click.argument('ticket_id', required=False)
def cli(ticket_id, action, auto_approve, force):
    """
    Process src.fedoraproject.org repository requests.

    Possible actions include "list", "process", "processall".

    Examples:

        fedscm-admin list

        fedscm-admin process 1

        fedscm-admin processall

        fedscm-admin process 1 --force
    """
    if force and action != 'process':
        raise click.ClickException('The force option can only be used when '
                                   'processing a single ticket')

    # Test that all the config items are set in config.ini
    for config_item in ['pagure_api_token', 'pagure_ticket_api_token',
                        'pdc_api_token']:
        fedscm_admin.config.get_config_item(CONFIG, config_item)

    if action == 'processall':
        # We need to authenticate to FAS to see if a package reviewer is a
        # packager
        login_to_fas_with_user_input()
        # We need to authenticate so we get the email addresses of the users
        # instead of their full names when viewing bugs
        login_to_bugzilla_with_user_input()
        process_all_tickets(auto_approve=auto_approve)
    elif action == 'process':
        if ticket_id is None:
            raise click.ClickException('You must specify a ticket ID')
        issue = fedscm_admin.pagure.get_issue(ticket_id)
        if issue is None or issue.get('status') != 'Open':
            raise click.ClickException(
                'The ticket does not exist or is closed')
        else:
            # We need to authenticate to FAS to see if a package reviewer is
            # a packager
            login_to_fas_with_user_input()
            # We need to authenticate so we get the email addresses of the
            # users instead of their full names when viewing bugs
            login_to_bugzilla_with_user_input()
            process_ticket(issue, force=force, auto_approve=auto_approve)
    elif action == 'list':
        list_all_tickets()


if __name__ == '__main__':
    cli()
