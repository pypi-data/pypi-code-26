# ------------------------------------------------------------------
#  <summary>
# FileName       : Tirrilee_Contact_Form/views.py
# Description    : Contact_Form 패키지에서 뷰 설정
# Special Logic  : None
# Copyright      : 2018 by Tirrlie Inc. All rights reserved.
# Author         : aiden@tirrilee.io, 2018-06-07
# Modify History : Just Created.
# </summary>
# ------------------------------------------------------------------

import logging

from django.http import HttpResponseBadRequest
from django.views.generic import FormView
from django.shortcuts import redirect, render
from .forms import ContactForm
from Tirrilee_Contact_Form import signals

logger = logging.getLogger('envelope.views')

class ContactView(FormView):
    form_class = ContactForm
    template_name = 'tirrilee_contact_form/contact_form.html'
    success_url = '/'
    form_kwargs = {}

    def get_form_kwargs(self):
        kwargs = super(ContactView, self).get_form_kwargs()
        kwargs.update(self.form_kwargs)
        return kwargs

    # Form 검증 성공
    def form_valid(self, form):
        responses = signals.before_send.send(sender=self.__class__,
                                             request=self.request,
                                             form=form)
        for (receiver, response) in responses:
            if not response:
                logger.warning("Rejected by %s", receiver.__name__)
                return HttpResponseBadRequest()
        form.save()
        return redirect(self.get_success_url())

    # Form 검증 실패
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

def filter_spam(sender, request, form, **kwargs):

    if issubclass(sender, ContactView):
        from .spam_filters import check_honeypot
        return check_honeypot(request, form)


signals.before_send.connect(filter_spam, dispatch_uid='Tirrilee_Contact_Form.views.filter_spam')