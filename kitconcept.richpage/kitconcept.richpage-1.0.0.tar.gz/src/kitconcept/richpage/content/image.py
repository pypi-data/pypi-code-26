# -*- coding: utf-8 -*-
from kitconcept.richpage import _
from zope import schema
from zope.interface import Interface
from plone.dexterity.content import Item
from zope.interface import implementer


class IImage(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False,
    )


@implementer(IImage)
class Image(Item):
    """ The Image content type """
