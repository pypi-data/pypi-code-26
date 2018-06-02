# -*- coding: utf-8 -*-
"""forms.py: Django datatableview_advanced_search"""

from __future__ import unicode_literals
from __future__ import print_function

import logging

from django import forms
from django.core import validators

from datatableview_advanced_search.models import DataTableUserColumns

__author__ = 'Steven Klass'
__date__ = '3/1/18 9:22 AM'
__copyright__ = 'Copyright 2018 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

