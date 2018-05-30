# -*- coding: utf-8 -*-
"""Terms & Conditions Widget Implementation"""

from plone import api
from plone.mls.listing.browser.tcwidget.interfaces import ITCWidget
from Products.Five.browser import BrowserView
from Products.Five.browser.metaconfigure import ViewMixinForTemplates
from z3c.form.browser.checkbox import SingleCheckBoxWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import FieldWidget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IBool


class RenderTCWidget(ViewMixinForTemplates, BrowserView):
    index = ViewPageTemplateFile('tcwidgetwrapper.pt')


@implementer_only(ITCWidget)
class TCWidget(SingleCheckBoxWidget):
    """Single Input type checkbox widget implementation."""

    klass = u'terms-conditions-widget'
    target = None

    def tc_link(self):
        if not self.target:
            return

        path = str(self.target)
        if path.startswith('/'):
            item = api.content.get(path=path)
        else:
            item = api.content.get(UID=path)
        if not item:
            return
        return {
            'label': item.title,
            'url': item.absolute_url(),
        }


@adapter(IBool, IFormLayer)
@implementer(IFieldWidget)
def TCFieldWidget(field, request):
    """IFieldWidget factory for TCWidget."""
    widget = FieldWidget(field, TCWidget(request))
    # widget.label = u''  # don't show the label twice
    return widget
