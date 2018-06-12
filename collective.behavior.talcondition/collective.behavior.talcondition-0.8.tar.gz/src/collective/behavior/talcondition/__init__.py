# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory
from plone import api

_ = MessageFactory('collective.behavior.talcondition')

PLONE_VERSION = int(api.env.plone_version()[0])


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
