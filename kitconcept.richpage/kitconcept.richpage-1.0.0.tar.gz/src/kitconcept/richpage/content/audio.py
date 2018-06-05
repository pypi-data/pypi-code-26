# -*- coding: utf-8 -*-
from plone.app.contenttypes import _
from plone.app.contenttypes.content import File
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class IAudio(model.Schema):
    """ The IAudio interface"""

    title = schema.TextLine(
        title=_(u"Titel"),
        description=u'Der Titel wird oberhalb des Audio-Players angezeigt.',
        required=False,
    )

    model.primary('file')
    file = namedfile.NamedBlobFile(
        title=_(u'label_file', default=u'Audio-Datei (.mp3)'),
        description=u'Die Audio-Datei muss das .mp3-Format haben.',
        required=True,
    )

    image = namedfile.NamedBlobImage(
        title=_(u'label_image', default=u'Bild'),
        description=u'Dieses Bild wird oberhalb des Audio-Players angezeigt.',
        required=False,
    )


@implementer(IAudio)
class Audio(File):
    """ The Audio content type """
