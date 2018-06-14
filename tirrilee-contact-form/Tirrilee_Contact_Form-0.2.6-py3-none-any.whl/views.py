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

from django.views.generic import FormView
from django.shortcuts import redirect, render
from .forms import ContactForm


# def ContactView(request):
#     return render(request, 'tirrilee_contact_form/contact_form.html', { 'form' : ContactForm} )


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'tirrilee_contact_form/contact_form.html'
    success_url = '/'

    def form_valid(self, form):
        """
        Sends the message and redirects the user to ``success_url``.
        """
        # responses = signals.before_send.send(sender=self.__class__,
        #                                      request=self.request,
        #                                      form=form)
        # for (receiver, response) in responses:
        #     if not response:
        #         logger.warning("Rejected by %s", receiver.__name__)
        #         return HttpResponseBadRequest()
        form.save()
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        """
        When the form has errors, display it again.
        """
        return self.render_to_response(self.get_context_data(form=form))