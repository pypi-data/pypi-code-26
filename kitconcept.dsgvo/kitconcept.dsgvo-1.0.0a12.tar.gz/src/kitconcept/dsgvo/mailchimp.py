# -*- coding: utf-8 -*-
from collective.mailchimp.browser.newsletter import NewsletterSubscriberForm
from plone.z3cform.fieldsets import extensible

from z3c.form import field

from zope import schema
from zope.component import adapts
from zope.interface import Interface

from kitconcept.dsgvo import _
from kitconcept.dsgvo.interfaces import IKitconceptDsgvoLayer
from kitconcept.dsgvo.interfaces import validateAccept
from kitconcept.dsgvo.widget import DsgvoSingleCheckBoxFieldWidget


class IDsgvoMailchimpSchema(Interface):

    dsgvo_accept = schema.Bool(
        title=_(u'label_dsgvo_mailchimp_accept',
                default=(
                    u'Ich habe die <a href="${portal_url}/datenschutz" '
                    u'target="_blank">'
                    u'Datenschutzerklärung und Widerrufhinweise</a> '
                    u'gelesen und akzeptiere diese.')),
        description=_(
            u'help_dsgvo_mailchimp_accept',
            default=u''),
        required=True,
        constraint=validateAccept,
    )


class NewsletterSubscriberFormExtender(extensible.FormExtender):
    adapts(Interface, IKitconceptDsgvoLayer, NewsletterSubscriberForm)

    def update(self):
        fields = field.Fields(IDsgvoMailchimpSchema)
        fields['dsgvo_accept'].widgetFactory = \
            DsgvoSingleCheckBoxFieldWidget
        self.add(fields)
