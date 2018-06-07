# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope import schema
from zope.interface import Interface
from zope.interface import Invalid
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from kitconcept.dsgvo import _


def validateAccept(value):
    if value is not True:
        raise Invalid(_(
            u'label_dsgvo_accept_invalid',
            default=(u'Bitte akzeptieren sie die Datenschutzerklärung und '
                     u'Widerrufhinweise.')))
    return True


class IKitconceptDsgvoLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IDsgvoUserDataSchema(Interface):

    dsgvo_accept = schema.Bool(
        title=_(u'label_dsgvo_mailchimp_accept',
                default=(
                    u'Ich habe die <a href="${portal_url}/datenschutz" '
                    u'target="_blank">'
                    u'Datenschutzerklärung und Widerrufhinweise</a> '
                    u'gelesen und akzeptiere diese.')),
        description=_(
            u'help_dsgvo_accept',
            default=u''),
        required=True,
        constraint=validateAccept,
    )
