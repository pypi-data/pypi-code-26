# -*- coding: utf-8 -*-
from kitconcept.richpage import _
from zope import schema
from zope.interface import Interface
from plone.dexterity.content import Item
from zope.interface import implementer


class IGoogleMap(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False,
    )

    google_map_embed_url = schema.TextLine(
        title=_(u"Google Map embed URL"),
        description=_(u"""1) Auf GoogleMaps gehen und in das Suchfeld eine Adresse eingeben.
2) Auf das Teilen-Symbol klicken und dann auf "Karte einbetten" gehen.
3) Es öffnet sich ein iframe-Code. Hier den Teil hinter src= zwischen den Anführungszeichen kopieren und hier einfügen."""), # noqa
        required=True,
    )


@implementer(IGoogleMap)
class GoogleMap(Item):
    """ The GoogleMap content type """
