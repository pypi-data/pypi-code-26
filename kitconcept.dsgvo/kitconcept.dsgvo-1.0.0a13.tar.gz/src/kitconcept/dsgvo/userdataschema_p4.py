# -*- coding: utf-8 -*-

from plone.app.form.widgets.checkboxwidget import CheckBoxWidget
from plone.app.users.browser.personalpreferences import UserDataConfiglet
from plone.app.users.browser.personalpreferences import UserDataPanel
from plone.app.users.browser.personalpreferences import UserDataPanelAdapter
from plone.app.users.browser.register import RegistrationForm
from plone.app.users.userdataschema import IUserDataSchema
from plone.app.users.userdataschema import IUserDataSchemaProvider

from zope import schema
from zope.i18nmessageid import Message
from zope.interface import implements

from kitconcept.dsgvo import _
from kitconcept.dsgvo.util import dsgvo_translate


class DsgvoCheckboxWidget(CheckBoxWidget):

    def __call__(self):
        if isinstance(self.context.title, Message):
            self.context.title = dsgvo_translate(self.context.title,
                                                 self.request)
        return super(DsgvoCheckboxWidget, self).__call__()


class InvalidAccept(schema.ValidationError):

    __doc__ = _(
            u'label_dsgvo_accept_invalid',
            default=(u'Bitte akzeptieren sie die Datenschutzerklärung und '
                     u'Widerrufhinweise.'))


def validateAccept(value):
    if value is not True:
        raise InvalidAccept()
    return True


class IDsgvoP4UserDataSchema(IUserDataSchema):
    '''
    Combined fields
    '''

    dsgvo_accept = schema.Bool(
        title=_(u'label_dsgvo_accept',
                default=(
                    u'Ich habe die <a href="${portal_url}/datenschutz" '
                    u'target="_blank">'
                    u'Datenschutzerklärung und Widerrufhinweise</a> '
                    u'gelesen und akzeptiere diese.')),
        description=_(
            u'help_dsgvo_accept',
            default=u''),
        required=True,
        constraint=validateAccept,
    )


class EnhancedUserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IDsgvoP4UserDataSchema


class EnhancedRegistrationForm(RegistrationForm):

    def __init__(self, context, request):
        super(EnhancedRegistrationForm, self).__init__(context, request)

    @property
    def form_fields(self):
        '''
        form_fields in the registration form is a property. We cannot
        modify self.form_fields.
        '''
        form_fields = super(EnhancedRegistrationForm, self).form_fields
        form_fields['dsgvo_accept'].custom_widget = DsgvoCheckboxWidget
        return form_fields


class DsgvoP4UserDataSchemaAdapter(UserDataPanelAdapter):

    def get_dsgvo_accept(self):
        return self.context.getProperty('dsgvo_accept', '')

    def set_dsgvo_accept(self, value):
        return self.context.setMemberProperties({'dsgvo_accept': value})

    dsgvo_accept = property(get_dsgvo_accept, set_dsgvo_accept)


class DsgvoUserDataPanel(UserDataPanel):

    def __init__(self, context, request):
        super(DsgvoUserDataPanel, self).__init__(context, request)
        self.form_fields = self.form_fields.omit('dsgvo_accept')


class DsgvoUserDataConfiglet(UserDataConfiglet):

    def __init__(self, context, request):
        super(DsgvoUserDataConfiglet, self).__init__(context, request)
        self.form_fields = self.form_fields.omit('dsgvo_accept')
