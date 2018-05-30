# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#

import logging
import traceback
from datetime import datetime

from ..runtime_storage import runtime
from ..utils import is_string

LOGGER = logging.getLogger(__name__)


_SQREEN_EVENT_PREFIX = 'sq.'

_TRACK_OPTIONS_FIELDS = frozenset([
    'properties',
    'user_identifiers',
    'timestamp',
])

_TRACK_PAYLOAD_SECTIONS = ('request', 'params', 'headers')

STACKTRACE_EVENTS = set()

_MAX_EVENT_PROPERTIES = 16


def track(event, options=None):
    if not is_string(event):
        raise TypeError("event name must be a string, not {}"
                        .format(event.__class__.__name__))
    if event.startswith(_SQREEN_EVENT_PREFIX):
        LOGGER.warning("Event names starting with %r are reserved, "
                       "event %r has been ignored",
                       _SQREEN_EVENT_PREFIX, event)
        return False
    if options is None:
        options = {}
    for option_key in list(options):
        if option_key not in _TRACK_OPTIONS_FIELDS:
            LOGGER.warning("Invalid option key %r, skipped", option_key)
            del options[option_key]
    if 'timestamp' not in options:
        timestamp = datetime.utcnow()
        options['timestamp'] = timestamp
    else:
        timestamp = options['timestamp']
        if not isinstance(timestamp, datetime):
            raise TypeError("timestamp option must be a datetime object, not {}"
                            .format(event.__class__.__name__))
    properties = options.get('properties')
    if properties and len(properties) > _MAX_EVENT_PROPERTIES:
        LOGGER.warning("Event %r has %d properties, "
                       "only the first %d ones will be reported",
                       event, len(properties), _MAX_EVENT_PROPERTIES)
        options = dict(options)
        options['properties'] = dict(sorted(properties.items())[:_MAX_EVENT_PROPERTIES])
    if event in STACKTRACE_EVENTS:
        LOGGER.debug("Stacktrace recorded by for event %s", event)
        options['stacktrace'] = traceback.format_stack()
    runtime.observe('sdk', [
        'track',
        timestamp,
        event,
        options,
    ], payload_sections=_TRACK_PAYLOAD_SECTIONS, report=True)
    return True
