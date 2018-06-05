# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from signoff.models import Document, DocumentConsent


def index(request):
    context = {}
    if request.user.is_authenticated:
        documents = Document.objects.with_user(request.user)
    else:
        documents = Document.objects

    context['documents'] = documents.all()
    context['current_documents'] = documents.only_active()

    return render(request, 'signoff/index.html', context)


@login_required
def view_document(request, id):
    document = get_object_or_404(Document.objects.with_user(request.user),
                                 id=id)

    context = {}
    context['document'] = document

    if document.user_consents:
        context['consent'] = document.user_consents[0]

    if request.method == 'POST':
        # Only record the signature if we don't already have one for this user
        if not document.user_consents:
            is_valid = True
            if not request.POST.get('consent_checkbox'):
                is_valid = False
                context['checkbox_error'] = True
            if request.POST.get('name') != request.user.get_full_name():
                is_valid = False
                context['name_error'] = True
            if is_valid:
                consent = DocumentConsent(
                    document=document,
                    user=request.user,
                    ip=request.META.get('REMOTE_ADDR'),
                    xff_header=request.META.get('HTTP_X_FORWARDED_FOR'),
                    signed_name=request.POST.get('name'),
                )
                consent.save()
            else:
                return render(request, 'signoff/document.html', context)


        return redirect('signoff:signoff_index')

    return render(request, 'signoff/document.html', context)
