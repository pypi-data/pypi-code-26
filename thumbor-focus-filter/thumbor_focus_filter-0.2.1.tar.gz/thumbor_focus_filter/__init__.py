#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

__version__ = '0.2.1'

try:
    from thumbor_focus_filter.focus import Filter  # NOQA
except ImportError:
    logging.exception('Could not import thumbor_focus_filter. Probably due to setup.py installing it.')
