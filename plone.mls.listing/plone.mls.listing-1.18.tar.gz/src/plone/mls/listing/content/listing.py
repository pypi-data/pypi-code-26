# -*- coding: utf-8 -*-
"""Dexterity based Listing content type."""

from plone.directives import form
from plone.mls.listing.i18n import _
from zope import schema


class IListing(form.Schema):
    """A single MLS Listing."""

    title = schema.TextLine(
        title=_(u'Title'),
    )

    listing_id = schema.TextLine(
        title=_(u'MLS Listing ID'),
    )
