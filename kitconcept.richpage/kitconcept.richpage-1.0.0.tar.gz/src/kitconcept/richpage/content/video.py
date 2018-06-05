# -*- coding: utf-8 -*-
from collective import dexteritytextindexer
from kitconcept.richpage import _
from plone.dexterity.content import Item
from plone.namedfile import field as namedfile
from plone.supermodel.model import Schema
from zope import schema
from zope.interface import implementer


class IVideo(Schema):
    """ The IVideo interface"""

    title = schema.TextLine(
        title=_(u"Title"),
        required=False,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
        missing_value=u'',
    )

    youtube_embed_url = schema.TextLine(
        title=_(u"Youtube embed URL"),
        description=_(
            u"Sie können entweder eine Youtube video URL oder eine Playlist hinzufügen"  # noqa
        ),
        required=True,
    )

    dexteritytextindexer.searchable('transcript_description')
    transcript_description = schema.Text(
        title=_(u"Transkript Beschreibung"),
        required=False,
    )

    dexteritytextindexer.searchable('transcript_title')
    transcript_title = schema.TextLine(
        title=_(u"Transkript Titel"),
        required=False,
    )

    transcript_file = namedfile.NamedBlobFile(
        title=_(u'Transkript Datei'),
        required=False,
    )


@implementer(IVideo)
class Video(Item):
    """ The Video content type """
