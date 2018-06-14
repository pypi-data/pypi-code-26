# ------------------------------------------------------------------
#  <summary>
# FileName       : Tirrilee-Contact-Form/forms.py
# Description    : Contact_Form 패키지에서 입력 폼 설정
# Special Logic  : None
# Copyright      : 2018 by Tirrlie Inc. All rights reserved.
# Author         : aiden@tirrilee.io, 2018-06-07
# Modify History : Just Created.
# </summary>
# ------------------------------------------------------------------

from django.template.loader import render_to_string
from .widgets import CustomTextInput, CustomTextarea, CustomFileInput
from smtplib import SMTPException
from django.core import mail
from django import forms
from .signals import after_send
from . import settings
import logging

logger = logging.getLogger('Tirrilee_Contact_Form.forms')

class ContactForm(forms.Form):

    name = forms.CharField(label="", max_length=100, widget=CustomTextInput('이름'))
    email = forms.EmailField(label="", widget=CustomTextInput('메일'))
    subject = forms.CharField(label="", max_length=250, widget=CustomTextInput('제목'))
    message = forms.CharField(label="", widget=CustomTextarea('내용'))
    file = forms.FileField(label="", widget= CustomFileInput, required=False)

    subject_intro = settings.SUBJECT_INTRO
    from_email = settings.FROM_EMAIL
    email_recipients = settings.EMAIL_RECIPIENTS
    template_name = 'tirrilee_contact_form/email_body.txt'
    html_template_name = 'tirrilee_contact_form/email_body.html'

    def __init__(self, *args, **kwargs):
        for kwarg in list(kwargs):
            if hasattr(self, kwarg):
                setattr(self, kwarg, kwargs.pop(kwarg))
        super(ContactForm, self).__init__(*args, **kwargs)

    def save(self):
        subject = self.get_subject()
        from_email = self.get_from_email()
        email_recipients = self.get_email_recipients()
        context = self.get_context()
        file = self.get_file()
        message_body = render_to_string(self.get_template_names(), context)
        print("메일 보내기")

        try:
            message = mail.EmailMultiAlternatives(
                subject=subject,
                body=message_body,
                from_email=from_email,
                to=email_recipients,
                headers={
                    'Reply-To': self.cleaned_data['email']
                }
            )
            if settings.USE_HTML_EMAIL:
                html_body = render_to_string(self.html_template_name, context)
                try:
                    message.attach(file.name, file.read(), file.content_type)
                except:
                    pass
                message.attach_alternative(html_body, "text/html")
            message.send()
            after_send.send(sender=self.__class__, message=message, form=self)
            logger.info("Contact form submitted and sent (from: %s)" %
                        self.cleaned_data['email'])
        except SMTPException:
            logger.exception("An error occured while sending the email")
            return False
        else:
            return True

    def get_context(self):

        return self.cleaned_data.copy()

    def get_subject(self):

        return self.subject_intro + self.cleaned_data['subject']

    def get_from_email(self):

        return self.from_email

    def get_email_recipients(self):

        return self.email_recipients

    def get_file(self):

        return self.cleaned_data['file']

    def get_template_names(self):

        return self.template_name
