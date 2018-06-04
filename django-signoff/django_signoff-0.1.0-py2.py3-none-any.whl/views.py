# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from django_signoff.models import Document, DocumentConsent


@login_required
def consent_index(request):
    context = {}
    context['documents'] = Document.objects.with_user(request.user).all()
    context['current_documents'] = Document.objects.with_user(request.user)\
                                           .only_active()

    return render(request, 'django_signoff/index.html', context)


@login_required
def consent_document(request, id):
    document = get_object_or_404(Document.objects.with_user(request.user),
                                 id=id)

    if request.method == 'POST' and request.POST.get('consent_checkbox'):
        # Only record the signature if we don't already have one for this user
        if not document.user_consents:
            consent = DocumentConsent(
                document=document,
                user=request.user,
                ip=request.META.get('REMOTE_ADDR'),
                xff_header=request.META.get('HTTP_X_FORWARDED_FOR'),
            )
            consent.save()

        return redirect('consent_index')

    context = {}
    context['document'] = document

    if document.user_consents:
        context['consent'] = document.user_consents[0]

    return render(request, 'django_signoff/document.html', context)
