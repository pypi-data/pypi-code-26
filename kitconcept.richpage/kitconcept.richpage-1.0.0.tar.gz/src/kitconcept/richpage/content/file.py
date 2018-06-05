# -*- coding: utf-8 -*-
from plone.app.contenttypes import _
from plone.app.contenttypes.content import File
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class IFile(model.Schema):
    """ The IFile interface"""

    title = schema.TextLine(
        title=_(u"Title"),
        required=False,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
        missing_value=u'',
    )

    model.primary('file')
    file = namedfile.NamedBlobFile(
        title=_(u'label_file'),
        required=True,
    )

    alternate_filename = schema.TextLine(
        title=_(u"Datei-Titel"),
        required=False,
    )


@implementer(IFile)
class File(File):
    """ The File content type """
