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
Initializes the module and provides helper functions
"""
from __future__ import absolute_import
from datetime import datetime
import re
from copy import deepcopy

import pkg_resources

import fedscm_admin.config

try:
    VERSION = pkg_resources.get_distribution('fedscm-admin').version
except pkg_resources.DistributionNotFound:
    VERSION = 'unknown'

MONITOR_CHOICES = ['no-monitoring', 'monitoring', 'monitoring-with-scratch']
STANDARD_BRANCH_SLAS = {
    'master': {
        'rawhide': '2222-01-01'
    },
    'epel7': {
        'stable_api': '2024-06-30',
        'security_fixes': '2024-06-30',
        'bug_fixes': '2024-06-30'
    },
    'el6': {
        'stable_api': '2020-11-30',
        'security_fixes': '2020-11-30',
        'bug_fixes': '2020-11-30'
    },
    'f28': {
        'bug_fixes': '2019-06-08',
        'security_fixes': '2019-06-08'
    },
    'f27': {
        'bug_fixes': '2018-12-14',
        'security_fixes': '2018-12-14'
    },
    'f26': {
        'security_fixes': '2018-07-01',
        'bug_fixes': '2018-07-01'
    },
    'f25': {
        'security_fixes': '2018-07-01',
        'bug_fixes': '2017-12-01'
    },
    'f24': {
        'security_fixes': '2017-08-11',
        'bug_fixes': '2017-08-11'
    }
}
INVALID_EPEL_ERROR = (
    'This package is already an EL package and is built on all supported '
    'arches, therefore, it cannot be in EPEL. If this is a mistake or you '
    'have an exception, please contact the Release Engineering team.')
today = datetime.utcnow().date()
# Remove any branches that have gone EOL since these were hardcoded. This data
# should really be in PDC, but there is not suitable API yet.
for branch, slas in deepcopy(STANDARD_BRANCH_SLAS).items():
    if not any([datetime.strptime(sla_eol, '%Y-%m-%d').date() >= today
                for sla_eol in slas.values()]):
        STANDARD_BRANCH_SLAS.pop(branch)

CONFIG = fedscm_admin.config.get_config()


# This is defined here to avoid circular imports
def is_epel(branch):
    """
    Determines if this is or will be an epel branch
    :param branch: a string of the branch name
    :return: a boolean
    """
    return bool(re.match(r'^(?:el|epel)\d+$', branch))


from fedscm_admin.fas import FASClient  # noqa: E402
FAS_CLIENT = FASClient()

from fedscm_admin.bugzilla import BugzillaClient  # noqa: E402
BUGZILLA_CLIENT = BugzillaClient()
