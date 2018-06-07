# -*- coding: utf-8 -*-
from Products.CMFPlone.browser.contact_info import ContactForm

from plone.supermodel import model
from plone.z3cform.fieldsets import extensible

from z3c.form import field

from zope import schema
from zope.component import adapts
from zope.interface import Interface

from kitconcept.dsgvo import _
from kitconcept.dsgvo.interfaces import IKitconceptDsgvoLayer
from kitconcept.dsgvo.widget import DsgvoSingleCheckBoxFieldWidget


class IDsgvoContactInfoSchema(model.Schema):

    dsgvo_contact_info_text = schema.Bool(
        title=_(
            u'label_dsgvo_info',
            default=(
                u'Ihre Anfrage wird verschlüsselt per https an unseren '
                u'Server geschickt. Sie erklären sich damit einverstanden, '
                u'dass wir die Angaben zur Beantwortung Ihrer Anfrage '
                u'verwenden dürfen. Hier finden Sie unsere '
                u'<a href="${portal_url}/datenschutz" '
                u'target="_blank">Datenschutzerklärung '
                u'und Widerrufhinweise</a>.')),
        description=_(
            u'help_dsgvo_info',
            default=u''),
        default=True,
    )


class ContactFormExtender(extensible.FormExtender):
    adapts(Interface, IKitconceptDsgvoLayer, ContactForm)

    def update(self):
        fields = field.Fields(IDsgvoContactInfoSchema)
        fields['dsgvo_contact_info_text'].widgetFactory = \
            DsgvoSingleCheckBoxFieldWidget
        self.add(fields)
