# -*- coding: utf-8 -*-
"""Plone support for MLS Listings."""

from plone import api


PLONE_4 = '4' <= api.env.plone_version() < '5'
PLONE_5 = '5' <= api.env.plone_version() < '6'

PRODUCT_NAME = 'plone.mls.listing'


class AnnotationStorage(dict):
    """Custom annotation dict for MLS configurations."""

    context = None
