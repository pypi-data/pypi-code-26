# -*- coding: utf-8 -*-
from collective import dexteritytextindexer
from kitconcept.richpage import _
from plone.dexterity.content import Container
from plone.supermodel.model import Schema
from zope import schema
from zope.interface import implementer


class IRichPage(Schema):

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    dexteritytextindexer.searchable('subtitle')
    subtitle = schema.TextLine(
        title=_(u"Subtitle"),
        required=False,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
        missing_value=u'',
    )


@implementer(IRichPage)
class RichPage(Container):
    """ The RichPage content type """
