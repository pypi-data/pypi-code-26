###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Text widget
$Id: gmap.py 4824 2018-04-24 09:33:55Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface

import z3c.form.interfaces
import z3c.form.widget

import m01.gmap.widget

from j01.form import interfaces
from j01.form.widget.widget import WidgetMixin


class GMapWidget(WidgetMixin, m01.gmap.widget.GMapWidget):
    """Text input type widget"""

    zope.interface.implementsOnly(interfaces.IGMapWidget)

    klass = u'gmap-control form-control'
    css = u'gmap'


class GeoPointGMapWidget(WidgetMixin, m01.gmap.widget.GeoPointGMapWidget):
    """Text input type widget"""

    zope.interface.implementsOnly(interfaces.IGeoPointGMapWidget)

    klass = u'gmap-point-control form-control'
    css = u'gmap-point'


# gmap
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getGMapWidget(field, request):
    """IFieldWidget factory for GMapWidget."""
    return z3c.form.widget.FieldWidget(field, GMapWidget(request))


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getGeoPointGMapWidget(field, request):
    """IFieldWidget factory for GMapWidget."""
    return z3c.form.widget.FieldWidget(field, GeoPointGMapWidget(request))
