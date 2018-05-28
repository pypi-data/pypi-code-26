# -*- coding: utf-8 -*-
"""
A viewlet rendering a dsgvo information banner
"""

from plone import api
from plone.app.layout.viewlets import common as base

from kitconcept.dsgvo import _
from kitconcept.dsgvo.util import dsgvo_translate


class DsgvoViewlet(base.ViewletBase):
    '''
    A viewlet to render a dsgvo information banner
    '''

    def info(self):
        msg = _(
            u'dsgvo_info_banner',
            default=(
                u'Um unsere Webseite für Sie optimal zu gestalten und '
                u'fortlaufend verbessern zu können, verwenden wir Cookies. '
                u'Durch die weitere Nutzung der Webseite stimmen Sie der '
                u'Verwendung von Cookies zu. Weitere Informationen zu '
                u'Cookies erhalten Sie in unserer '
                u'<a href="${portal_url}/datenschutz" target="_blank">'
                u'Datenschutzerklärung</a>.'),
                )
        return dsgvo_translate(msg, self.request)

    def portal_url(self):
        return api.portal.get().absolute_url()

    # def render(self):
    #     cookie = self.request.cookies.get('hide-dsgvo-banner', False)
    #     if cookie:
    #         return ''
    #     return super(DsgvoViewlet, self).render()
