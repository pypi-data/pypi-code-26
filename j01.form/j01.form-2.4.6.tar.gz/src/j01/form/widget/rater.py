###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Text widget
$Id: rater.py 4844 2018-04-29 15:48:28Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component

import z3c.form.widget
import z3c.form.interfaces

import j01.rater.widget
import j01.rater.interfaces

from j01.form import interfaces
from j01.form.layer import IFormLayer
from j01.form.widget.widget import WidgetMixin


class RatingWidget(WidgetMixin, j01.rater.widget.RatingWidget):
    """RatingWidget widget"""

    zope.interface.implementsOnly(interfaces.IRatingWidget)

    klass = u'j01-rater-control j01-rater-five-star-control form-control'
    css = u'j01-rater'


class FiveStarRatingWidget(RatingWidget):
    """FiveStarRatingWidget widget"""

    zope.interface.implementsOnly(interfaces.IFiveStarRatingWidget)

    klass = u'j01-rater-control j01-rater-five-star-control form-control'
    css = u'j01-rater'

    increment = 1
    isHalfStar = False


class FiveHalfStarRatingWidget(RatingWidget):
    """FiveHalfStarRatingWidget widget"""

    zope.interface.implementsOnly(interfaces.IFiveHalfStarRatingWidget)

    klass = u'j01-rater-control j01-rater-five-half-star-control form-control'
    css = u'j01-rater'

    increment = 0.5
    isHalfStar = True


class FiveHalfStarFullRatingWidget(RatingWidget):
    """FiveHalfStarFullRatingWidget widget"""

    zope.interface.implementsOnly(interfaces.IFiveHalfStarFullRatingWidget)

    klass = u'j01-rater-control j01-rater-five-half-star-control form-control'
    css = u'j01-rater'

    increment = 1
    isHalfStar = True


# get
@zope.component.adapter(j01.rater.interfaces.IFiveStarRatingField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getFiveStarRatingWidget(field, request):
    """IFieldWidget factory for IFiveStarRatingWidget."""
    return z3c.form.widget.FieldWidget(field, FiveStarRatingWidget(request))


@zope.component.adapter(j01.rater.interfaces.IFiveHalfStarRatingField,
    IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getFiveHalfStarRatingWidget(field, request):
    """IFieldWidget factory for IFiveHalfStarRatingWidget."""
    return z3c.form.widget.FieldWidget(field, FiveHalfStarRatingWidget(request))


@zope.component.adapter(j01.rater.interfaces.IFiveHalfStarFullRatingField,
    IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getFiveHalfStarFullRatingWidget(field, request):
    """IFieldWidget factory for IPasswordWidget."""
    return z3c.form.widget.FieldWidget(field,
        FiveHalfStarFullRatingWidget(request))
